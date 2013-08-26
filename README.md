#GceCondor

A python script that helps start and terminate a basic Condor cluster on Google Compute Engine (GCE).

MIT's excellent Starcluster library was used as inspiration to start this; currently, GceCondor is just a teeny-tiny subset of
 Starcluster's functionality. One day Starcluster may support GCE, but for now I am using these scripts to get a Condor
 cluster up and running on GCE.

The long-term project goal is to make it easy to have a super-computer be summoned on-the-fly when needed for a task.
GCE currently has several advantages over EC2 for doing this:

1.  Being billed by the minute instead of hour makes the cost considerations easier to figure out for a given task.
2.  We have had very high reliability on GCE instances compared to EC2 so far, especially regarding Spot instances.
3.  We have seen much better performance per core when using single core instances versus multi core instances for our
tasks.  GCE currently offers single core instances. More info on this issue [here][3].

Bring on the Singularity.

##Installation

1. Install [Google API's Library for Python][4], [gsutil][5], and [gcutil][5].
2. Download and unpack gce_condor zip.
3. Upload *startup.sh*, *master_00debconf*, and *node_00debconf* to your Google Cloud Storage Bucket.
4. In *gce_condor.py*, set `PROJECT_ID` to the name of your project and `CS_BUCKET` to the name of your bucket. You
can also change other settings in there like zone, machine type, etc later as needed, but these two changes are required.

##Usage


*WARNING: This is very alpha code that starts up things that charge dinero by the minute.  Double-check via Console
or gcutil that the instances are actually terminated when you want them to be!*

Before you run gce_condor, you will need to create and place a *client_secrets.json* file in the same
 directory. Directions for creating the *clients_secrets.json* file are [here][1].

###Examples:

####To create a 10 node cluster:

    ./gce_condor.py start 10

####To terminate the cluster:

    ./gce_condor terminate

*WARNING:  currently this terminates ALL instances in the project. If you have other stuff going on in your project,
you will need to manually delete the instances for now. Like I said, very alpha code...*

####To create a 10 node cluster from image:

This command uses custom images instead of a start up script to create the instances. This *should* be faster than a
boot using a start-up script, especially as more software is needed to be on the instance.

    /gce_condor.py start -i 10

*Note:  Before you run this option, you will need to create and store the master and node customer images in your bucket and set
the name of the images in `MASTER_IMAGE_NAME` and `NODE_IMAGE_NAME`.  The master and node instances to make the custom image
are the instances created by this script without the `-i` option.  So just run gce_condor without `-i` to create the instances,
and then save an image of the master and node. You can use any node instance.  Directions for saving a custom image from an
instance are [here][2]*.

####To access the cluster

If you want to, you know, actually use the cluster, you will need to use [gcutil][6]:

Access the master instance:

    gcutil ssh master

Access one of the node instances:

    gctuil ssh node001

##Advanced Detail

###Booting from start-up script vs custom image

When issuing the default `./gce_condor start` command without the `-i` option, the file *startup.sh* is used as a start up script for
 each instance.  *startup.sh* installs Condor using debian's apt-get installer, puts the master and node debian
 configuration files on the appropriate instances, and restarts Condor.

When using the `-i` option, the instances are instead booted from their respective images specified in `MASTER_IMAGE_NAME` and
 `NODE_IMAGE_NAME`. This means that the files *startup.sh*, *master_00debconf*, and *node_00debconf* are NOT used.
 As explained in the next couple sections, any time these files are changed, the images must be updated to reflect
 those changes (if a boot from image is desired).

###Adding software to the instances

To install new software such as *gfortran* or *numpy*, add the appropriate line in *startup.sh*.  If boot from image is
 desired, you will have to first run `gce_condor.py` once without the `-i` option to create the instances from
 newly configured start-up script, and then make the updated images from these instances.


###Condor Configuration
In the almost certain event that you need to configure Condor to your liking, you will need to modify the master__00debconf
and node_00debconf files. If boot from image is desired, you will have to first run `gce_condor.py` once without
the `-i` option to create the instances from newly configured start-up script, and then make the updated images from these instances.


##Dependencies

1. [Google APIs Client Library for Python][4]
2. [gsutil][5]
3. [gcutil][6]


[1]: https://developers.google.com/compute/docs/api/python_guide#authorization
[2]: https://developers.google.com/compute/docs/images#installinganimage
[3]: http://stackoverflow.com/questions/17007062/memory-intense-jobs-scaling-poorly-on-multi-core-cloud-instances-ec2-gce-rack
[4]: https://code.google.com/p/google-api-python-client/
[5]: https://developers.google.com/storage/docs/gsutil_install
[6]: https://developers.google.com/compute/docs/gcutil/#install