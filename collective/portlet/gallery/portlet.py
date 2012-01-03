from zope import component
from zope import schema
from zope import interface
from zope.formlib import form

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base
from plone.portlet.static import static

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.gallery import messageFactory as _
from collective.portlet.gallery import ploneMessageFactory as _p

class IGalleryPortlet(IPortletDataProvider):
    """A portlet which can display galleries."""

    header = schema.TextLine(
        title=_p(u"Portlet header"),
        description=_p(u"Title of the rendered portlet"),
        required=True)

    

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

    omit_border = False
    footer = u""
    more_url = ''

    def __init__(self, header=u"", omit_border=False, footer=u"",
                 more_url=''):
        self.header = header
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url

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


class AddForm(base.AddForm):
    """add form"""
    form_fields = form.Fields(IGalleryPortlet)
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
    label = _(u"title_edit_portlet",
              default=u"Edit gallery portlet")
    description = _(u"description_portlet",
                    default=u"A portlet which can display galleries.")
