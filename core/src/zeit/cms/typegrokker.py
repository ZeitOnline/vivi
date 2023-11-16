import martian
import zeit.cms.interfaces
import zeit.cms.type
import zeit.connector.interfaces
import zeit.connector.resource
import zope.component.zcml


def annotate_interface(interface, key, value):
    interface.setTaggedValue(key, value)


class TypeGrokker(martian.ClassGrokker):
    martian.component(zeit.cms.type.TypeDeclaration)

    def execute(self, context, config, **kw):
        context = context()
        if context.interface is None:
            return False

        if context.type is not None:
            # Resource -> Content
            zope.component.zcml.adapter(
                config,
                (context.content,),
                zeit.cms.interfaces.ICMSContent,
                (zeit.connector.interfaces.IResource,),
                name=context.type,
            )

            # Content -> Resource
            zope.component.zcml.adapter(
                config,
                (context.resource,),
                zeit.connector.interfaces.IResource,
                (context.interface,),
            )

            # To lookup the TypeDeclaration object by type name
            zope.component.zcml.utility(
                config, zeit.cms.interfaces.ITypeDeclaration, context, name=context.type
            )

        # Annotate interface
        register_as_type = context.register_as_type
        if callable(register_as_type):
            register_as_type = register_as_type(config)
        if register_as_type:
            config.action(
                discriminator=('annotate_interface', context.interface, 'zeit.cms.type'),
                callable=annotate_interface,
                args=(context.interface, 'zeit.cms.type', context.type_identifier),
            )
            config.action(
                discriminator=('annotate_interface', context.interface, 'zeit.cms.title'),
                callable=annotate_interface,
                args=(context.interface, 'zeit.cms.title', context.title),
            )
            config.action(
                discriminator=('annotate_interface', context.interface, 'zeit.cms.addform'),
                callable=annotate_interface,
                args=(context.interface, 'zeit.cms.addform', context.addform),
            )
            if context.addpermission:
                config.action(
                    discriminator=(
                        'annotate_interface',
                        context.interface,
                        'zeit.cms.addpermission',
                    ),
                    callable=annotate_interface,
                    args=(context.interface, 'zeit.cms.addpermission', context.addpermission),
                )
            zope.component.zcml.interface(config, context.interface, context.interface_type)

        def type_declaration_factory(an_instance):
            return context

        zope.component.zcml.adapter(
            config,
            (type_declaration_factory,),
            provides=zeit.cms.interfaces.ITypeDeclaration,
            for_=(context.interface,),
        )

        return True
