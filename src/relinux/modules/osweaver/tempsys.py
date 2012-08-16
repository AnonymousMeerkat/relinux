'''
Generates a temporary filesystem to hack on
@author: Anonymous Meerkat
'''

from relinux import logger, config, configutils, fsutil, pwdmanip, aptutil, numrange
from relinux.modules.osweaver import configs, aptcache
import os
import shutil
import re
import threading

tmpsys = config.TempSys
#tmpsystree = "TempSysTree"
#cpetcvar = "EtcVar"
#remconfig = "RemConfig"
#remcachedlists = "RemCachedLists"
#remtempvar = "RemTempVar"
#genvarlogs = "GenVarLogs"
#remusers = "RemUsers"


# Generate the tree for the tempsys
tmpsystree = {"deps": [], "tn": "TempSysTree"}
class genTempSysTree(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(tmpsystree["tn"])

    def run(self):
        logger.logI(self.tn, _("Generating the tree for the temporary filesystem"))
        fsutil.maketree([tmpsys + "etc", tmpsys + "dev",
                          tmpsys + "proc", tmpsys + "tmp",
                          tmpsys + "sys", tmpsys + "mnt",
                          tmpsys + "media/cdrom", tmpsys + "var", tmpsys + "home"], self.tn)
        fsutil.chmod(tmpsys + "tmp", "1777", self.tn)
tmpsystree["thread"] = genTempSysTree()


# Copy the contents of /etc/ and /var/ to the tempsys
cpetcvar = {"deps": [tmpsystree], "tn": "EtcVar"}
class copyEtcVar(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(cpetcvar["tn"])

    def run(self):
        logger.logI(self.tn, _("Copying files to the temporary filesystem"))
        excludes = configutils.getValue(configs[configutils.excludes])
        fsutil.fscopy("etc", tmpsys + "etc", excludes, self.tn)
        fsutil.fscopy("var", tmpsys + "var", excludes, self.tn)
cpetcvar["thread"] = copyEtcVar()


# Remove configuration files that can break the installed/live system
remconfig = {"deps": [cpetcvar], "tn": "RemConfig"}
class remConfig(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(remconfig["tn"])

    def run(self):
        # Remove these files as they can conflict inside the installed system
        logger.logV(self.tn, _("Removing personal configurations that can break the installed system"))
        fsutil.rmfiles([tmpsys + "etc/X11/xorg.conf*", tmpsys + "etc/resolv.conf",
                        tmpsys + "etc/hosts", tmpsys + "etc/hostname", tmpsys + "etc/timezone",
                        tmpsys + "etc/mtab", tmpsys + "etc/fstab",
                        tmpsys + "etc/udev/rules.d/70-persistent*",
                        tmpsys + "etc/cups/ssl/server.crt", tmpsys + "etc/cups/ssl/server.key",
                        tmpsys + "etc/ssh/ssh_host_rsa_key", tmpsys + "etc/ssh/ssh_host_dsa_key.pub",
                        tmpsys + "etc/ssh/ssh_host_dsa_key", tmpsys + "etc/ssh/ssh_host_rsa_key.pub",
                        tmpsys + "etc/group", tmpsys + "etc/passwd", tmpsys + "etc/shadow",
                        tmpsys + "etc/shadow-", tmpsys + "etc/gshadow", tmpsys + "etc/gshadow-",
                        tmpsys + "etc/wicd/wired-settings.conf",
                        tmpsys + "etc/wicd/wireless-settings.conf", tmpsys + "etc/printcap",
                        tmpsys + "etc/cups/printers.conf"])
remconfig["thread"] = remConfig()


# Remove cached lists
remcachedlists = {"deps": [cpetcvar], "tn": "RemCachedLists"}
class remCachedLists(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(remcachedlists["tn"])

    def run(self):
        logger.logV(self.tn, _("Removing cached lists"))
        fsutil.adrm(tmpsys + "var/lib/apt/lists/",
                    {"excludes": True, "remdirs": False, "remsymlink": True, "remfullpath": False},
                    ["*.gpg", "*lock*", "*partial*"], self.tn)
remcachedlists["thread"] = remCachedLists()


# Remove temporary files in /var
remtempvar = {"deps": [cpetcvar], "tn": "RemTempVar"}
class remTempVar(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(remtempvar["tn"])

    def run(self):
        logger.logV(self.tn, _("Removing temporary files in /var"))
        # Remove all files in these directories (but not directories inside them)
        for i in ["etc/NetworkManager/system-connections/", "var/run", "var/log", "var/mail",
                  "var/spool", "var/lock", "var/backups", "var/tmp", "var/crash", "var/lib/ubiquity"]:
            fsutil.adrm(tmpsys + i,
                        {"excludes": False, "remdirs": False, "remsymlink": True, "remfullpath": False},
                        None, self.tn)
remtempvar["thread"] = remTempVar()


# Generate logs in /var/log
genvarlogs = {"deps": [cpetcvar], "tn": "GenVarLogs"}
class genVarLogs(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(genvarlogs["tn"])

    def run(self):
        # Create the logs
        logger.logV(self.tn, _("Creating empty logs"))
        for i in ["dpkg.log", "lastlog", "mail.log", "syslog", "auth.log", "daemon.log", "faillog",
                          "lpr.log", "mail.warn", "user.log", "boot", "debug", "mail.err", "messages", "wtmp",
                          "bootstrap.log", "dmesg", "kern.log", "mail.info"]:
            logger.logVV(logger.MTab + _("Creating") + " " + i)
            fsutil.touch(tmpsys + "var/log/" + i)
genvarlogs["thread"] = genVarLogs()


# Edit passwd and shadow files to remove users
remusers = {"deps": [cpetcvar], "tn": "RemUsers"}
class remUsers(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(remusers["tn"])

    # Helper function for changing the /etc/group file
    def _parseGroup(self, i, usrs):
        addme = True
        for x in usrs:
            # Removes all groups the "offending" user created for itself
            if i["group"] == x["user"]:
                addme = False
                return
            # Removes the user from all groups it is inside
            if x["user"] in i["users"]:
                i["users"].remove(x["user"])
        if addme is True:
            return [True, pwdmanip.PGtoEntry(i)]
        else:
            return [False, ""]

    # Helper function for changing the /etc/shadow file
    def _parseShadow(self, i, usrs):
        addme = True
        for x in usrs:
            # Removes the "offending" user
            if i["user"] == x["user"]:
                addme = False
                return
        if addme is True:
            return [True, pwdmanip.PStoEntry(i)]
        else:
            return [False, ""]

    def run(self):
        # Setup the password and group stuff
        logger.logI(self.tn, _("Removing conflicting users"))
        passwdf = tmpsys + "etc/passwd"
        #passwdfile = open(passwdf, "r")
        #passwdstat = fsutil.getStat(passwdf)
        #passwdbuffer = configutils.getBuffer(passwdfile)
        #passwdfile.close()
        #passwdfile = open(passwdf, "w")
        buffers = fsutil.ife_getbuffers(passwdf)
        pe = pwdmanip.parsePasswdEntries(buffers[3])
        buffers[3] = pe
        # Users to "delete" on the live system
        logger.logV("Gathering users to remove")
        nobody = ""
        for x in pe:
            if x["user"] == "nobody":
                nobody = x
        if nobody == "":
            logger.logE(self.tn, _("User 'nobody' could not be found!"))
        max_uid = 1999
        sysrange = 500
        nuid = int(nobody["uid"])
        if nuid <= 100:
            # nobody has been assigned to the conventional system UID range
            max_uid = 1999
            sysrange = 100
        elif nuid < 500:
            # nobody has been assigned to the RHEL system UID range
            max_uid = 1999
            sysrange = 500
        elif nuid >= 65530 and nuid <= 65535:
            # nobody has been assigned to the highest possible unsigned short integer (16 bit) range
            max_uid = nuid - 1
            sysrange = 555
        elif nuid >= 32766:
            # nobody has been assigned to the highest possible signed short integer (16 bit) range
            max_uid = nuid - 1
            sysrange = 500
        else:
            max_uid = 1999
            sysrange = 555
        usrs = pwdmanip.getPPByUID(numrange.gen_num_range(sysrange, max_uid), pe)
        if config.VVStatus is False:
            logger.logV(_("Removing them"))
        logger.logVV(_("Removing users in /etc/passwd"))
        fsutil.ife(buffers, lambda line: [True, pwdmanip.PPtoEntry(line)] if not line in usrs else [False, ""])
        # Rewrite the password file
        #for i in ppe:
        #    if not i in usrs:
        #        passwdfile.write(pwdmanip.PPtoEntry(i))
        #fsutil.copystat(passwdstat, passwdf)
        #passwdfile.close()
        # Now for the group file
        logger.logVV(self.tn, _("Removing users in /etc/group"))
        groupf = tmpsys + "etc/group"
        buffers = fsutil.ife_getbuffers(groupf)
        pe = pwdmanip.parseGroupEntries(buffers[3])
        fsutil.ife(buffers, lambda line: self._parseGroup(line, usrs))
        # Work on both shadow files
        shadowf = tmpsys + "etc/shadow"
        gshadowf = tmpsys + "etc/gshadow"
        buffers = fsutil.ife_getbuffers(shadowf)
        gbuffers = fsutil.ife_getbuffers(gshadowf)
        pe = pwdmanip.parseShadowEntries(buffers[3])
        buffers[3] = pe
        # If you look carefully (or just do a quick google search :P), you will notice that gshadow files
        # are very similar to group files, so we can just parse them as if they were group files
        pe = pwdmanip.parseGroupEntries(gbuffers[3])
        gbuffers[3] = pe
        logger.logVV(self.tn, _("Removing users in /etc/shadow"))
        fsutil.ife(buffers, lambda line: self._parseShadow(line, usrs))
        logger.logVV(self.tn, _("Removing users in /etc/gshadow"))
        fsutil.ife(gbuffers, lambda line: self._parseGroup(line, usrs))
        logger.logI(self.tn, _("Applying permissions to casper scripts"))
remusers["thread"] = remUsers()


# Edits casper.conf
casperconf = {"deps": [cpetcvar], "tn": "casper.conf"}
class CasperConfEditor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(casperconf["tn"])

    # Helper function
    def __varEditor(self, line, lists):
        patt = re.compile("^.*? *([A-Za-z_-]*?)=.*$")
        m = patt.match(line)
        #if configutils.checkMatched(m):
        if m.group(0) is not None:
            for i in lists.keys():
                if m.group(1) == i:
                    lists[i] = None
                    return [True, i + "=" + lists[i]]
        return [False, ""]

    # Casper Variable Editor
    # lists - Dictionary containing all options needed
    def _varEditor(self, files, lists):
        buffers = fsutil.ife_getbuffers(files)
        fsutil.ife(buffers, lambda line: self.__varEditor(line, lists))
        # In case the file is broken, we'll add the lines needed
        buffers = open(files, "a")
        for i in lists:
            if lists[i] is not None:
                buffers.write("export " + i + "=" + lists[i] + "\n")
        buffers.close()

    def run(self):
        # Edit the casper.conf
        # Strangely enough, casper uses the "quiet" flag if the build system is either Debian or Ubuntu
        if config.VStatus is False:
            logger.logI(self.tn, _("Editing casper and LSB configuration files"))
        logger.logV(self.tn, _("Editing casper.conf"))
        buildsys = "Ubuntu"
        if configutils.parseBoolean(configutils.getValue(configs[configutils.casperquiet])) is False:
            buildsys = ""
        unionfs = configutils.getValue(configs[configutils.unionfs])
        if unionfs == "overlayfs" and aptutil.compVersions(aptutil.getPkgVersion(aptutil.getPkg("casper", aptcache)), "1.272", aptutil.lt):
            logger.logW(self.tn, _("Using DEFAULT instead of overlayfs"))
            unionfs = "DEFAULT"
        self.varEditor(tmpsys + "etc/casper.conf", {
                                            "USERNAME": configutils.getValue(configs[configutils.username]),
                                            "USERFULLNAME":
                                                configutils.getValue(configs[configutils.userfullname]),
                                            "HOST": configutils.getValue(configs[configutils.host]),
                                            "BUILD_SYSTEM": buildsys,
                                            "FLAVOUR": configutils.getValue(configs[configutils.flavour]),
                                            "UNIONFS": unionfs})
        logger.logV(self.tn, _("Editing lsb-release"))
        self.varEditor(tmpsys + "etc/lsb-release", {
                                    "DISTRIB_ID": configutils.getValue(configs[configutils.sysname]),
                                    "DISTRIB_RELEASE": configutils.getValue(configs[configutils.version]),
                                    "DISTRIB_CODENAME": configutils.getValue(configs[configutils.codename]),
                                    "DISTRIB_DESCRIPTION":
        configutils.getValue(configs[configutils.description])})
casperconf["thread"] = CasperConfEditor()


# Sets up Ubiquity
ubiquitysetup = {"deps": [cpetcvar], "tn": "Ubiquity"}
class UbiquitySetup(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tn = logger.genTN(ubiquitysetup["tn"])

    def run(self):
        # If the user-setup-apply file does not exist, and there is an alternative, we'll copy it over
        logger.logI(self.tn, _("Setting up the installer"))
        if os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply.orig") and not os.path.isfile("/usr/lib/ubiquity/user-setup/user-setup-apply"):
            shutil.copy2("/usr/lib/ubiquity/user-setup/user-setup-apply.orig",
                         "/usr/lib/ubiquity/user-setup/user-setup-apply")
        if configutils.parseBoolean(configutils.getValue(configs[configutils.aptlistchange])) is True:
            fsutil.makedir(tmpsys + "usr/share/ubiquity/")
            aptsetup = open(tmpsys + "usr/share/ubiquity/apt-setup", "w")
            aptsetup.write("#!/bin/sh\n")
            aptsetup.write("exit\n")
            aptsetup.close()
        else:
            fsutil.makedir(tmpsys + "usr/lib/ubiquity/apt-setup/generators/")
            cdrom = open(tmpsys + "usr/lib/ubiquity/apt-setup/generators/40cdrom", "w")
            cdrom.write("#!/bin/sh\n")
            cdrom.write("exit\n")
            cdrom.close()
ubiquitysetup["thread"] = UbiquitySetup()


class TempSys(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deps = [tmpsystree]
        self.threadname = "TempSys"
        self.tn = logger.genTN(self.threadname)

    def run(self):
        logger.logI(self.tn, _("Removing unneeded files"))
        '''cbs = "/usr/share/initramfs-tools/scripts/casper-bottom/"
        # This pattern should do the trick
        execme = glob.glob(os.path.join(cbs, "[0-9][0-9]*"))
        for i in execme:
            logger.logVV(self.tn, "chmod 755 " + i)
            fsutil.chmod(i, "755")'''


# Thread list
threads = [tmpsystree, cpetcvar, remconfig, remcachedlists, remtempvar, genvarlogs, remusers,
           casperconf, ubiquitysetup]
