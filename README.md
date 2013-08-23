#GceCondor

A python script that helps start and terminate a simple Condor cluster on Google Compute Engine (GCE).

MIT's excellent Starcluster library was used as inspiration to start this; currently, this is just a teeny-tiny subset of
 that functionality. One day Starcluster may support GCE, but for now I am using these simple scripts to get my Condor
 cluster up and running on GCE.

A basic code summary:  Given the number of instances, *gce_condor.py* uses *startup.sh* as a start up script for
 each instance.  *startup.sh* installs Condor using debian's apt-get installer and then puts the master and node debian
 configuration files on the appropriate instances.

The long-term project goal is to make it easy to have a super-computer be summoned on-the-fly when needed for a task.
GCE currently has several advantages over EC2 for doing this:

1.  Being billed by the minute instead of hour makes the cost considerations easier to figure out for a given task.
2.  We have had very high reliability on GCE instances compared to EC2 so far, especially regarding Spot instances.
3.  We have seen much better performance per core when using single core instances versus multi core instances for our
tasks.  GCE currently offers single core instances. More info on this issue [here][3].


##Installation

1. Upload *startup.sh*, *master_00debconf*, and *node_00debconf* to your Google Cloud Storage Bucket.
2. In *gce_condor.py*, set `PROJECT_ID` to the name of your project and `CS_BUCKET` to the name of your bucket.

##Usage


*WARNING: This is very alpha code that starts up things that charge money by the minute.  Double-check via Console
 console or gcutil that the instances are actually terminated when it says it is!*

Before you run gce_condor, you will need to create and place a *client_secrets.json* file in the same
 directory. Directions for creating the *clients_secrets.json* file are [here][1].

###Examples:

####To create a 10 node cluster:

    ./gce_condor.py start 10

####To terminate the cluster:

    .gce_condor terminate

*WARNING:  currently this terminates ALL instances in the project. If you have other stuff going on in your project,
you will need to manually delete the instances for now. Like I said, very alpha code...*

####To create a 10 node cluster from image:

This command uses custom images instead of a start up script to create the instances. This *should* be faster, especially
 as more software is needed on the instance.

    /gce_condor.py start -i 10

*Note:  Before you run this option, you will need to create and store the master and node customer images in your bucket and set
the name of the images in `MASTER_IMAGE_NAME` and `NODE_IMAGE_NAME`.  The master and node instances to make the custom image
are the instances created by this script without the `-i` option.  So just run gce_condor without `-i` to create the instances,
and then save an image of the master and node. You can use any node instance.  Directions for saving a custom image from an
instance are [here][2]*.

##Dependencies

1. gcutil



[1]: https://developers.google.com/compute/docs/api/python_guide#authorization
[2]: https://developers.google.com/compute/docs/images#installinganimage
[3]: http://stackoverflow.com/questions/17007062/memory-intense-jobs-scaling-poorly-on-multi-core-cloud-instances-ec2-gce-rack