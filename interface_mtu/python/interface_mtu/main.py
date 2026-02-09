# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        service_name = service.name
        service_mtu = service.mtu
        vars = ncs.template.Variables()
        for device in service.device:
            device_name = device.name
            self.log.info(f"Device Name: {device_name}")
            device_ned_id = root.ncs__devices.device[device_name].device_type.generic.ned_id
            self.log.info(f'NED_ID={device_ned_id}')
            for interface in device.interfaces:
                if device_ned_id == "nokia-srlinux_gnmi-gen-1.2:nokia-srlinux_gnmi-gen-1.2":
                    int_type = "ethernet-"
                elif device_ned_id == "cisco-nx_nc-gen-1.0:cisco-nx_nc-gen-1.0":
                    int_type = "eth"
                else:
                    int_type = interface.type
                vars.add('NAME', service_name)
                vars.add('MTU', service_mtu)
                vars.add('DEVICE', device_name)
                vars.add('TYPE', int_type)
                template = ncs.template.Template(interface)
                template.apply('interface_mtu-template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('interface_mtu-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
