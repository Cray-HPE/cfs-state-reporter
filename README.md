Configuration Management Framework State Reporter
=============

About
-----

The purpose of this tool is to inform the configuration management framework service (CMF)
of the initial unconfigured state of a node during boot. This allows CFS to bring the
node into a state of known good configuration during initial clean boot, as well, to
restore configuration to prescribed configuration in the event of a loss of power.

The responsibility of this client is to successfully communicate that the node is
without configuration ONCE to CFS.