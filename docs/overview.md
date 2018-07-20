# Introduction

This document explains the things a DorpsGek 'bot' should be able to do.

# Goals

## Major goals

* Support a Pull Request workflow to GitHub
* Support IRC about stuff that happens on GitHub
* Support CI functionality to GitHub
* Support CD functionality to OpenTTD for non-game related stuff
* Support releases from Pull Requests and tags

## Minor goals

* Prepare for AWS


# Details for selected goals

## Support a Pull Request workflow to GitHub
Currently we are using the GitHub workflow for Pull Request.
Over the last few weeks, we noticed several issues.
If you mark a Pull Request as "needs work", it becomes rather unclear when you have to look at the patch again.
Mostly, as only the person who marked the "needs work" can unmark it.
As more people look at Pull Request, it is not unlikely that another developer finishes the review of a Pull Request.
We rather use labels, where we can label a Pull Request for the state it is in.
For example: needs-review, needs-changes, needs-testing, need-opinion-of-other-dev, etc.
Using GitHub Apps and a custom bot allows us to do this.
There are many other projects who already use this; rarely they made their bot available for reuse by other projects.

## Support IRC about stuff that happens on GitHub
Currently #openttd.notice is informed of Pull Request created etc, but the channel has to be without +nt.
This means it is not possible getting this information into #openttd, as abuse without +nt is just around the corner.
Having a dedicated bot that tells when stuff happens on GitHub is very much welcomed.
It also goes the other way around.
Being able to say: @gh 6767, which produces a full link to GitHub Issue/Pull Request 6767 is very useful.
Other things to consider are things like: @build 6767, which produces downloadable binaries for that Pull Request.

## Support CI functionality to GitHub
When a Pull Request is opened/updated, a CI should be triggered.
Currently this is done by a almost-not-configurable-plugin of Jenkins.
It uses the JenkinsFile from the repository that triggered.
This is very dangerous, as it might launch a cryptominer.
It is much more safe to have first something that generates a script based on some file in the repository, and execute that.
Sadly, the current plugin doesn't allow that at all; as such, we need to write some custom code to do this ourself.

## Support CD functionality to OpenTTD for non-game related stuff
When a new version of OpenTTD-Website, OpenTTD-BaNaNaS2, OpenTTD-DorpsGek, OpenTTD-MS2-AS is pushed into master (or a tag), it should automatically deploy a new version to a staging area, so it can be validated, and pushed live.
Some as with OpenTTD-CF, after merging it should build the new images and push them.
This is called a CD (Continues Delivery), and would greatly increase the tempo of changes, without people knowing the technical compelxity of the setup.
Existing systems like Heroku (or the Open Source variant Dokku) show how this process can work.

## Support releases from Pull Requests and tags
Often on Pull Request we would like to download the binary so we can test if it does what it claims.
But doing this for every Pull Request is unwanted waste of CPU.
In many GitHub projects you see they added a bot to which they can say: "bot, run tests", etc.
A new command: "bot, make release" of some sorts would be very useful.
After compiling the binaries, it should be added as a comment to the Pull Request.
This can be done with a GitHub Apps.
Additionally, when ever a tag is created in OpenTTD, that tag should be compiled and published immediatly.
Basically, the CD variant for OpenTTD itself.
There is no need for any manual interactions, as a tag always means a new release.
This can also be used for Patchpacks etc, in similar fashion.
Nightlies can be created from master in the same way, but only once every NN hours on change.

## Prepare for AWS
Ideal we make this all compatible with AWS, so a migration to AWS is simple.
Mainly this holds for the build slaves, as using Spot Instances can greatly increase the CI time, with very little cost.

