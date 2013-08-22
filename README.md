#GceCondor

A class that helps set up and shutdown a simple Condor cluster on Google Compute Engine (GCE)

MIT's excellent Starcluster library was used as inspiration for starting this, although this just a teeny-tiny subset of
that functionality. One day Starcluster may support GCE, but for now I am using these simple scripts.

##Installation

1. Upload *startup.sh*, 'master_00debconf', and 'node_00debconf' to you Google Cloud Storage Bucket.

2.

