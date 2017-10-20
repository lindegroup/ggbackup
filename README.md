# ggbackup
This tool is built for automated backups of Google Groups with their settings and members.  While Google Apps Manager can perform that function, some administrators may not want to grant GAM the extensive API access it requires to run properly.

When run, the script will create a folder with the name of the G Suite domain and generate the following files:

* `settings.csv` - a CSV containing all the Groups and their settings
* `[group]_members.csv` - CSVs for each group containing their members and member configuration

## Compatibility
This tool is tested with Python 2.7 on MacOS.  It should be compatible with Python 3.5+ and should be fully cross-platform, but it hasn't been tested in other environments.

## Google API Scopes
To run properly, this tool needs access to the following APIs:

* Admin SDK API
* Groups Settings API

When authenticating the application with OAuth2, it will only request access to the following scopes:

* admin.directory.group.readonly
* admin.directory.group.member.readonly
* apps.groups.settings

While the Groups Settings scope technically grants read-write access to group settings, the application only makes read requests.

## Installation
Prerequisites:

* Python 2.7
* pip
* virtualenv (optional)

It's generally best practice to set up a virtualenv for each Python application to avoid dependency conflicts, but this is not required.

Once you download the application, change to its working directory and run the following command: `pip install -r requirements.txt`.  This will install all dependencies.

## Configuration
Once installed, the application needs to be configured both in G Suite and locally.

### G Suite Configuration
1.  Enable the APIs
    1. Log into [admin.google.com](https://admin.google.com) as an administrator for your domain.
    1. Go to the Security panel
    1. In the API Reference section, Enable API access and save.
1. Provision the application
    1. Navigate to [console.developers.google.com](https://console.developers.google.com) (you should still be logged in to your G Suite domain).
    1. Create a new project.
        1. Click to the right of the "Google APIs" heading where it will either say "Select a Project" or be on a previously created project.
        1. Click the "+" on the project selection window.
        1. Name the project (ggbackup is a good choice)
    1. Configure the OAuth Consent Screen.
        1. Once you've selected the ggbackup project, click "Credentials" on the left panel.
        1. Click the "OAuth consent screen" tab.
        1. Choose a Product name to show to users (GGBackup is a good choice).
        1. Click Save.
    1. Generate Application Credentials.
    	1. Still in the Credentials panel, click the "Credentials" tab.
    	1. Click the "Create credentials" button, then "OAuth Client ID"
    	1. Click "Other" then choose a name (ggbackup is a good choice)
    	1. Click "Save"
    1. Download the `client_secrets.json`
    	1. On the Credentials tab, you should see the application you just created.
    	1. On the far right, you'll see a download icon; this will download the `client_secrets.json` file for the application on this domain.  Save the file, you'll need it for configurating the local application.
	1. Turn on the APIs
	    1. In the same GGBackup product, click "Library" in the left panel.
	    1. Search for "Admin SDK" and enable it.
	    1. Go back to "Library"
	    1. Search for "Groups Settings API" and enable it.
	
### Local Configuration
The following optional steps will store your OAuth credentials locally for headless operation.

1. Locate the `client_secrets.json` file you downloaded above.
2. Run the following command: `python ggbackup.py --client_secrets [client_secrets.json] --setup [G Suite Domain]` (substitute the location of the client_secrets file and the primary domain for your G Suite instance).
3. A browser window will open.  Authenticate as an administrator for your G Suite domain.  You'll be presented with a code; paste it in the application.
4. The application will generate a file named `credentials.json` in your working directory.

## Usage
### Basic Usage
`python ggbackup.py [G Suite Domain Name]`

By default, the script will look for `client_secrets.json` and `credentials.json` in the working directory.  You can specify alternate locations for these files using the `--client_secrets` and `--credentials` flags, respectively.

By default, the script will create a directory with the G Suite primary domain name in your working directory and will store all CSVs there.

### Advanced Usage
The following arguments are available:

#### Positional arguments:

* `domain` - **REQUIRED** - the G Suite domain name to retrieve groups from

#### Logging arguments:

* `-v` - Verbose logging
* `--debug` - Debug logging

#### File location arguments:

* `--client_secrets CLIENT_SECRETS` - specify a different `client_secrets.json` file (default: `./client_secrets.json`)
* `--credentials CREDENTIALS` - specify a different `credentials.json` file (default: `./credentials.json`)
* `--target TARGET` - specify a different target directory for CSV file directory (defaults to the current working directory)

#### Authentication arguments:

* `--first` - Performs the full OAuth2 request; will not attempt to load credentials from a file.
* `-s`, `--save` - Save credentials to a file (implies `--first`)
* `--setup` - Only set up the application and do not request data.  Implies `--first` and `--save`.

#### Run options:

* `--nosettings` - Do not retrieve Group Settings (the legacy Google Apps Free edition does not support the Group Settings API).
* `--datestamp` - Add an ISO date stamp to the to the end of each CSV created.

*Copyright (c) 2017 [The Linde Group, Inc.](https://lindegroup.com)*
