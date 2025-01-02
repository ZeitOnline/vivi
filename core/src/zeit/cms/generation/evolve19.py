from zeit.cms.generation.install import installLocalUtility
import zeit.cms.generation


def update(root):
    import zeit.authentication.azure

    installLocalUtility(
        root,
        zeit.authentication.azure.PersistentTokenCache,
        'azure-token-cache',
        zeit.authentication.azure.ITokenCache,
    )


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
