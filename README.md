#GceCondor

A python script that helps set up and shutdown a simple Condor cluster on Google Compute Engine (GCE)

MIT's excellent Starcluster library was used as inspiration for starting this, although this just a teeny-tiny subset of
 that functionality. One day Starcluster may support GCE, but for now I am using these simple scripts.

A basic summary:  *gce_condor.py* uses *startup.sh* as a start up script for the GCE instance.  *startup.sh* installs
 condor using debian's apt-get installer and then puts the master and node debian configuration files on the appropriate
 instances.

*WARNING: This alpha code that starts GCE instances that cost money.  Double-check via Google's cloud console or
gcutil that the instances are actually shutdown when you think they are.*

##Installation

1. Upload *startup.sh*, *master_00debconf*, and *node_00debconf* to your Google Cloud Storage Bucket.
2. In *gce_condor.py*, set `PROJECT_ID` to the name of your project and `CS_BUCKET` to the name of your bucket.

##Usage

Before you run gce_condor, you will need to create and place a *client_secrets.json* file in the same
 directory. Directions for creating the *clients_secrets.json* file are [here][1].

###Examples:

####To create a 10 node cluster:

    ./gce_condor.py start 10

####To terminate the cluster:

    .gce_condor terminate

*WARNING:  currently this terminates ALL instances in the project. If you have other stuff going on in your project,
you will need to manually delete the instances for now. Like I said, alpha code...*

####To create a 10 node cluster from image:

    /gce_condor.py start -i 10

*Note:  Before you run this option, you will need to create and store the master and node customer images in your bucket and set
the name of the images in `MASTER_IMAGE_NAME` and `NODE_IMAGE_NAME`.  The instances to make the custom image from are just the
master and node instances created by this script (without the '-i' option).  You can use any node instance.  Directions
for saving a custom image from an instance are [here][2]*.

##Dependencies

1. gcutil


[1]: https://developers.google.com/compute/docs/api/python_guide#authorization
[2]: https://developers.google.com/compute/docs/images#installinganimage