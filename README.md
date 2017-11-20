# Riverscapes S3 Data Tools

This is a simple proof-of-concept tool to get people started with uploading projects into S3 buckets.

## Installation

### Step 1: Get your environment CMD shell (Windows-only)

On windows you need to make sure you are in a bash terminal with:
* Access to **[pip](https://pip.pypa.io/en/stable/installing/)**. See instructions on how to install QGIS and you can use the console console `.cmd` file from that.
* You need to have git installed and your `PATH` environment **must** reference the git installation.

### Step 2: AWS CLI

The [AWS Command Line Interface](https://aws.amazon.com/cli/?sc_channel=PS&sc_campaign=acquisition_CA&sc_publisher=google&sc_medium=command_line_b&sc_content=aws_cli_p&sc_detail=aws%20cli&sc_category=command_line&sc_segment=161196437474&sc_matchtype=p&sc_country=CA&s_kwcid=AL!4422!3!161196437474!p!!g!!aws%20cli&ef_id=WFHksAAABLc1JG8i:20161215003248:s) needs to be installed and configured with keys that can access the AWS resources you will be using.

There are straightforward installation instructions on their website. When it's installed simply run `aws configure` on the command line.

Use your Key and Secret key along with `us-west-2` as the region. For output format just leave the default whatever it is.

```
c:\> aws configure
AWS Access Key ID [****************32NS]:
AWS Secret Access Key [****************SgEe]:
Default region name [us-west-2]:
Default output format [json]:
```

### Step 2: Install `riverscapestools` with pip (Everyone)

```
pip install git+https://github.com/Riverscapes/riverscapestools
```

You know it worked when you get output for any/all of the following commands:

```
rspupload -h
rspdownload -h
rsplist -h
```

### Riverscapes Project Uploader

The project uploader reads the `project.rs.xml` from inside the the `program` folder you specify and tries to find a place for it in the repo based on a `Program.xml` file. The output is verbose and it asks you to confirm everything before it uploads anything.

Uploads are tested against what's already in the bucket using MD5 and only new files get uploaded.

**NB: If you want a "sync" where S3 files are deleted if they don't exist locally you need to use `—delete`**

```
usage: rspupload [-h] [--program PROGRAM] [--logfile LOGFILE] [--delete]
                 [--force] [--verbose]
                 project

positional arguments:
  project            Path to the project folder containing the project xml
                     file

optional arguments:
  -h, --help         show this help message and exit
  --program PROGRAM  Path or url to the Program XML file (optional)
  --logfile LOGFILE  Write the results of the operation to a specified logfile
                     (optional)
  --delete           Remote files that are not on local will be deleted
                     (disabled by default)
  --force            Force a download, even if files are the same (disabled by
                     default)
  --verbose          Get more information in your logs (optional)
```

### Riverscapes Project Downloader

The project downloader is designed to help you download any project in the S3 bucket

Uploads are tested against what's already in the bucket using MD5 and only new files get uploaded.

**NB: If you want a "sync" where S3 files are deleted if they don't exist on S3 you need to use `—delete`. Use with caution**

```
usage: rspdownload [-h] [--datadir DATADIR] [--program PROGRAM]
                   [--logfile LOGFILE] [--delete] [--force] [--verbose]

optional arguments:
  -h, --help         show this help message and exit
  --datadir DATADIR  Local path to the root of the program on your local
                     drive. You can omit this argument if you have `RSDATADIR`
                     set as an environment variable.
  --program PROGRAM  Path or url to the Program XML file (optional)
  --logfile LOGFILE  Write the results of the operation to a specified logfile
                     (optional)
  --delete           Local files that are not on S3 will be deleted (Default:
                     False).
  --force            Force a download, even if files are the same (disabled by
                     default)
  --verbose          Get more information in your logs.
```



### Riverscapes Project Lister

The project lister is designed to recurse efficiently through the bucket structure and list projects of a certain type in the bucket. It uses the `Program.xml` to find projects. If projects are not where they're supposed to be they will not be listed

```
usage: rsplist [-h] [--program PROGRAM] [--logfile LOGFILE] [--verbose]
               project

positional arguments:
  project            Name of the program we are looking for.

optional arguments:
  -h, --help         show this help message and exit
  --program PROGRAM  Path or url to the Program XML file (optional)
  --logfile LOGFILE  Write the results of the operation to a specified logfile
                     (optional)
  --verbose          Get more information in your logs (optional)
```


### Developing

To install as a local pip install 

``` bash
pip install -e . --user

```

### Bugs:

Pleae file bugs on [GitHub Issue Tracker](https://github.com/Riverscapes/riverscapestools/issues)
