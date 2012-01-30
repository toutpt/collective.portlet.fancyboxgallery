from zope import component
from zope import schema
from zope import interface
from zope.formlib import form


from AccessControl import getSecurityManager

from plone.memoize.instance import memoize
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base
from plone.portlet.static import static

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.fancyboxgallery import messageFactory as _
from collective.portlet.fancyboxgallery import ploneMessageFactory as _p

class IGalleryPortlet(IPortletDataProvider):
    """A portlet which can display galleries."""

    header = schema.TextLine(
        title=_p(u"Portlet header"),
        description=_p(u"Title of the rendered portlet"),
        required=True)

    target_gallery = schema.Choice(
        title=_(u"Target gallery"),
        description=_(u"Find the gallery which provides the photos to display"),
        required=True,
        source=SearchableTextSourceBinder(
            {'portal_type': ['Topic','Link','Folder']},
            default_query='path:'))

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the text above "
                      "without the standard header, border or footer."),
        required=True,
        default=False)

    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Text to be shown in the footer"),
        required=False)

    more_url = schema.ASCIILine(
        title=_(u"Details link"),
        description=_(u"If given, the header and footer "
                      "will link to this URL."),
        required=False)

class Assignment(base.Assignment):
    interface.implements(IGalleryPortlet)

    header = _(u"title_portlet", default=u"Gallery portlet")

    target_gallery = None
    omit_border = False
    footer = u""
    more_url = ''

    def __init__(self, header=u"", omit_border=False, footer=u"",
                 more_url='', target_gallery=None):
        self.header = header
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url
        self.target_gallery =target_gallery

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header

class Renderer(static.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('portlet.pt')
    gallery_template = ViewPageTemplateFile('gallery.pt')

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = component.getUtility(IIDNormalizer)
        return "portlet-gallery-%s" % normalizer.normalize(header)

    def has_link(self):
        return bool(self.data.more_url)

    def has_footer(self):
        return bool(self.data.footer)

    def photos(self):
        pcontext = self.target()
        view = component.getMultiAdapter((self.context, self.request),
                                         name="gallery")
        return view.photos()

    def render_gallery(self):
        return self.gallery_template()

    @memoize
    def gallery(self):
        target_path = self.data.target_gallery
        if not target_path:
            return None

        if target_path.startswith('/'):
            target_path = target_path[1:]

        if not target_path:
            return None

        portal_state = component.getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(target_path, unicode):
            # restrictedTraverse accepts only strings
            target_path = str(target_path)

        result = portal.unrestrictedTraverse(target_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result

    def gallery_view(self):
        return component.queryMultiAdapter((self.gallery(), self.request),
                                           name="gallery")

class AddForm(base.AddForm):
    """add form"""
    form_fields = form.Fields(IGalleryPortlet)
    form_fields['target_gallery'].custom_widget = UberSelectionWidget

    label = _(u"title_add_portlet",
              default=u"Add gallery portlet")
    description = _(u"description_portlet",
                    default=u"A portlet which can display galleries.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IGalleryPortlet)
    form_fields['target_gallery'].custom_widget = UberSelectionWidget

    label = _(u"title_edit_portlet",
              default=u"Edit gallery portlet")
    description = _(u"description_portlet",
                    default=u"A portlet which can display galleries.")
