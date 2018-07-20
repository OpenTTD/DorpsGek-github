# Introduction

This document explains why this repository implements its own
Continuous Deployment system, and how this is done.

It is Open Source and meant for Open Source projects. It was initially written
for OpenTTD (https://www.openttd.org/) but by no means limited to that. One
of the cornerstones of this bot is that it allows any fork or other project
related to OpenTTD to also benefit from the workflow it provides. As such the
decision was made to make the bot as generic as possible, and only using
OpenTTD as initial user of the project.

# Motivation

Understanding the complex infrastructure of a decent-sized Open Source
community is often not for the weak. Parts of the infrastructure can be the
main website, account management, in-game services, GitHub Apps,
Continuous Integration Tools, etc. Often only a few know and understand it,
meaning that changes to any of these services are slow and heavily depending
on those few.

Often opening up such infrastructures also increases the risk of abuse, and
decreases the trust one can have in, for example, the published binaries.

Still, to allow anyone with the correct permissions to contribute to these
services, without them understanding the complexity of these systems, a
Continuous Deployment system needs to be in place. With such a system, a
simple merge of a Pull Request can start a chain of events leading to a new
version of a website coming online.

Additionally, it is very likely that a fork of an Open Source project also
wants to benefit from the CI/CD, have their own website, etc. Having a system
in place that adds no additional cost to allow more projects on the same
system, becomes more and more important.

There are many systems that provide Continuous Deployment (CD), even a few
integrate it into their Continuous Integration (CI) (or integrate their CI
into their CD). Those systems are often very powerful and can do anything
you would like from a CI/CD, are available from highly configurable to fully
automated, and range from on-premise solutions to as-a-service solutions.

Given as this CI/CD is meant for Open Source projects, and should also work
on any fork thereof, security is a big factor. It should be as difficult as
possible for anyone with bad intentions to abuse the system. Many of the
existing CI/CD systems don't take this enough into account, in our opinion,
and either have a System Operations (SysOp) team monitoring their network,
or put that work to the Open Source project itself. But more work for either
SysOp or the Open Source project itself is why a CD was deemed necessary.
Open Source projects often don't have enough security-aware people to either
monitor their systems or counter such abuse, and only puts more pressure on
the few, instead of the many.

Of course preventing abuse completely is not possible; but by reducing the
chance on it, it also reduces the load on any SysOp team, and any possible
additional cost because of the abuse.

With all these constraints in mind, this CD was created. It is designed to
have a near-zero footprint from a SysOp perspective, while still allowing
anyone with sufficient permissions to roll out new websites, in-game services,
GitHub Apps, CI tooling, etc. without compromising security too much. It also
allows any fork to work with it, or in fact, any other project.

This does come at a penalty; everything runs in a Docker to get the most
practical isolation without sacrificing too much performance. Of course
starting a Docker for every silly task isn't free. There is a balance here
between security, performance, and maintenance.

# Implementation

This repository implements a GitHub Apps bot, with has many jobs. One of these
jobs is to acts as an orchestrator for the whole CI/CD. It is mainly meant
for CD, but CI can piggyback on the same infrastructure.

This is also because both the CI and CD are mostly reactive to what happens
on GitHub. That said, by no way is this implementation limited to GitHub;
it is trivial to support any other system, as long as it can emit events on
actions taken.

To execute commands, Runners are used. These Runners are small processes on
other machines (in Dockers) to do the real work. This allows us to distribute
the work over multiple machines (and even into the cloud), while ensuring
everything is isolated.

Everything this bot does is isolated (mainly by delegating it to Runners),
with the exception of fetching sources from GitHub. Although there is a small
security concern here (for example the recent
[Git CVE](https://nvd.nist.gov/vuln/detail/CVE-2018-11235) show there is a
potential security risk), it is considered low enough to not isolate this
at this moment in time.

## Domain separation

This bot serves different services. For example, one part handles the
GitHub Apps events. Another part handles communication with the Runners.

To have a clear domain separation between those services, each service
is handled by a single HTTP server; and there is no direct cross-talk between
them. Although it is easily possible to implement it in a single HTTP server,
there are a few advantages to split it up.

By having several HTTP servers, no developer can by accident allow information
to sneak from one domain to the other, without being explicit about it. Also
it makes the public-facing ones easier to monitor, and to restrict the private
ones by keeping them, well, private.

This also means that the private ones can have lower security measurements.
For example, GitHub Apps events have signatures which are validated, so we are
sure that the events are emitted by GitHub. A private connection doesn't need
to have this security measurement, making the implementation easier.

The same argument can be made for authentication; private connections are
easier to trust than public connections. As such, for example, GitHub Apps
have two layers of authentication. Runner connections have none.

Later additions can introduce more HTTP servers; for example, to communicate
with a bot that connects to IRC. Another possibility is one that communicates
with a frontend. Every time a new domain is added, it will run its own HTTP
server, and is clearly classified as a public or private one.

## What are Runners?

Runners run in one single environment. All jobs are configured to run in one
of these environment. This bot distributes the jobs over the available Runners
for their environment. Example of environments are: testing, staging,
production.

All Runners have restrictions, depending on the environment they are running
in. Runners that run in the testing environment for example, cannot execute
deployments. They can however build a Docker, or run a Docker that validates
source (but not run a Docker that is  reachable from the Internet).

Another example, the Runners in staging/production cannot build a Docker, nor
can they run a Docker to validate sources. They can only handle running Docker
images that are reachable from the Internet.

## Orchestration

This bot orchestrates everything. Runners can only execute simply commands,
and this bot asks the right Runners to execute them in the right order,
depending on the Repository and Configuration.

As example, a deployment will roll over to the new version of the Docker
image, while keeping enough information to roll back. It also prevents a
Docker image from upgrading in production if it wasn't upgraded in staging
yet.

Everything in this bot is modular and easy to extend. All actions are in
small functions; as such it is both easy to validate what they do, as easy to
extend if needed.
 
## Per Repository configuration

As every repository will be different, a configuration file is created to tell
this bot how the CI/CD should look. After investigation in current CI/CD
solutions already available, the GitLab CI/CD configuration format
(https://docs.gitlab.com/ee/ci/yaml/) matches best what this bot should be
able to do. As such, the configuaration is a subset of these specifications.

The biggest exception is that `script` is not available for most projects;
instead a command `dorpsgek` exists which takes care of most of the work.
For example, `dorpsgek: build` takes care of all the work to create and publish
the image for the given repository. See further documentation for this and all
other `dorpsgek` commands.

To follow suite with many other projects, this configuration file is called
`.dorpsgek.yml`.
