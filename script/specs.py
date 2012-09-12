#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, shutil, time, subprocess, platform
from optparse import OptionParser
from xml.dom.minidom import parseString

def builder_for(platform_type):
    if platform.system() == 'Windows':
        dir = os.getenv('USERPROFILE') + "/AppData/Roaming/Titanium/mobilesdk/win32/"
    else:
        dir = "/Library/Application\ Support/Titanium/mobilesdk/osx/"

    return "%s/%s/%s/builder.py" %(dir, sdk_version(), platform_type) 
    
def project_dir():
    return resource_dir().replace("Resources", "")

def resource_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return re.sub("Resources.+$", "Resources", script_dir)

def sdk_version():
    setting_path = os.path.join(project_dir(), ".settings", "com.appcelerator.titanium.mobile.prefs")
    version = ''
    version_constant_name = "MOBILE_PROJECT_SDK_VERSION"
    
    if os.path.exists(setting_path):
        for line in open(setting_path, 'r'):
            if line.startswith(version_constant_name):
                version = re.sub(version_constant_name + "=", "", line.strip())
    else:
        tag_name = 'sdk-version'
        setting_path = os.path.join(project_dir(), "tiapp.xml")
        f = open(setting_path, "r")
        data = f.read()
        f.close()
        tag = parseString(data).getElementsByTagName(tag_name)[0].toxml()
        version = tag.replace('<%s>' % tag_name, '').replace('</%s>' % tag_name, '')
        
    return version

def options_temporary_path():
    return os.path.join(resource_dir(), 'temp_runner_options.js')

def app_js_path():
    return os.path.join(resource_dir(), 'app.js')

def app_js_backup_path():
    return app_js_path() + ".backup"

def jasmine_titanium_app_console_js_path():
    return os.path.join(resource_dir(), 'vendor', 'jasmine-titanium', 'lib', 'jasmine-titanium-app-console.js')

def jasmine_titanium_app_webview_js_path():
    return os.path.join(resource_dir(), 'vendor', 'jasmine-titanium', 'lib', 'jasmine-titanium-app-webview.js')

def save_options_to_temporary(options, args):
    class_name = options.class_name
    verbose = options.is_verbose

    f = open(options_temporary_path(), "w")
    f.write("var runner_options = { classname:'%(class_name)s', verbose:'%(verbose)s' };" % locals())
    f.close()

def remove_temporary():
    os.remove(options_temporary_path())

def setup_jasmine_titanium_app_console_js():
    shutil.copyfile(app_js_path(), app_js_backup_path())
    shutil.copyfile(jasmine_titanium_app_console_js_path(), app_js_path())

def setup_jasmine_titanium_app_webview_js():
    shutil.copyfile(app_js_path(), app_js_backup_path())
    shutil.copyfile(jasmine_titanium_app_webview_js_path(), app_js_path())

def restore_app_js():
    shutil.copyfile(app_js_backup_path(), app_js_path())
    os.remove(app_js_backup_path())

def create_option_parser():
    parser = OptionParser(usage = "Usage: specs.py [options] [files or directories]")

    parser.add_option("-v", "--verbose", dest="is_verbose", 
            help="print spec detail.", action="store_true", default='')

    parser.add_option("-s", "--spec", dest="class_name", 
            help="specify class name", default="", metavar="CLASS_NAME")

    parser.add_option("-o", "--out", dest="output", 
            help="write output to a file instead of STDOUT.", default="", metavar="FILE")

    parser.add_option("-p", "--platform", dest="platform", 
            help="android or iphone. android is experimantal [default: iphone]", default="iphone", metavar="PLATFORM")

    parser.add_option("--android-sdk", dest="android_sdk_path", 
            help="specify android sdk path. ", default="", metavar="ANDROID_SDK_PATH")

    parser.add_option("-r", "--reporter", dest="reporter", 
            help="display result to html or console. html is experimantal(html only for android) [defulat: console]", default="console", metavar="REPORTER")

    return parser

def run(platform):
    return False
    # not implemented

def run_iphone_simulator():
    system_command_path = builder_for("iphone")

    if os.path.exists(system_command_path):
        command_path = system_command_path
    else:
        user_command_path = "~" + system_command_path
        command_path = user_command_path

    if platform.system() == 'Windows':
        command_path = "python %s" % command_path

    command = command_path + " run " + project_dir()
    os.system(command)

def run_android_emulator(android_sdk_path):
    if android_sdk_path == '':
        print "Please specify Android SDK Path."
        return False

    system_command_path = builder_for("android")

    if os.path.exists(system_command_path):
        command_path = system_command_path
    else:
        user_command_path = "~" + system_command_path
        command_path = user_command_path

    if platform.system() == 'Windows':
        command_path = "python %s" % command_path

    command = command_path + " run " + project_dir() + " " + android_sdk_path
    print "Installing..."
    output = subprocess.check_output(command, shell=True)
    print output

def main(argv):
    parser = create_option_parser()
    # TODO: read default option by .specs
    (options, args) = parser.parse_args(argv)

    save_options_to_temporary(options, args)

    if options.output:
        log = os.open(options.output, os.O_WRONLY|os.O_CREAT)
        os.dup2(log, sys.stdout.fileno())

    if options.reporter == 'console' and options.platform != 'android':
        setup_jasmine_titanium_app_console_js()
    else:
        setup_jasmine_titanium_app_webview_js()

    if options.platform == 'android':
        run_android_emulator(options.android_sdk_path)
    else:
        run_iphone_simulator()

    restore_app_js()
    remove_temporary()

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
