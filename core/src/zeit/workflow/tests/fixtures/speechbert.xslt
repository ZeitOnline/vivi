<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:string="http://exslt.org/strings"
  >

  <xsl:param name="url"/>

  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:template match="text()"/>
  <xsl:template match="text()" mode="body"/>
  <xsl:template match="text()" mode="authors"/>
  <xsl:template match="text()" mode="tags"/>

  <!-- We try to be whitespace-sensitive with the xsl tag placement,
       so the output looks nice. -->

<xsl:template match="/article">{
  "url": "<xsl:value-of select="$url"/>", <xsl:apply-templates />
  "authors": [<xsl:apply-templates mode="authors" />],
  "tags": [<xsl:apply-templates mode="tags" />],
  "body": [<xsl:apply-templates mode="body" />]
}
</xsl:template>

<xsl:template match="head" mode="authors">
     <xsl:for-each select="author[not(role)]">
         "<xsl:value-of select="display_name" />"<xsl:if test="position() != last()">, </xsl:if>
     </xsl:for-each>
</xsl:template>

<xsl:template match="head/rankedTags" mode="tags">
    <xsl:for-each select="tag">
        "<xsl:value-of select="." />"<xsl:if test="position() != last()">, </xsl:if>
    </xsl:for-each>
</xsl:template>

<xsl:template match="head/attribute[@name='uuid']">
  "uuid": "<xsl:value-of select="substring-before(substring(., 11), '}')"/>",</xsl:template>

<xsl:template match="head/attribute[@name='date_first_released']">
  "publishDate": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[@name='date_last_published_semantic']">
  "lastModified": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[@name='genre']">
  "genre": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[@name='audio_speechbert']">
  "hasAudio": "<xsl:apply-templates mode="tobool" select="node()" />",</xsl:template>
<xsl:template match="head/attribute[(@ns='http://namespaces.zeit.de/CMS/document') and (@name='ressort')]">
  "section": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[(@ns='http://namespaces.zeit.de/CMS/document') and (@name='sub_ressort')]">
  "subsection": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[@name='serie']">
  "series": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[@name='channels']">
  "channels": "<xsl:value-of select="."/>",</xsl:template>
<xsl:template match="head/attribute[@name='access']">
  "access": "<xsl:value-of select="."/>",</xsl:template>
<!-- XXX ToDo Replace genre by den '<genre> von <author/display_name(s)>' Artikeltyp -->
<!-- Info: image variant is guessed: is working currently but not forever -->
<xsl:template match="head/image">
  "image": "<xsl:value-of select="string:replace(./@base-id, 'http://xml.', 'https://img.')" />wide__820x461__desktop",</xsl:template>
<xsl:template match="body/title">
  "headline": "<xsl:value-of select="string:replace(string:replace(., '&#10;', '\n'), '&quot;', '\&quot;')"/>",</xsl:template>
<xsl:template match="body/subtitle">
  "subtitle": "<xsl:value-of select="string:replace(string:replace(., '&#10;', '\n'), '&quot;', '\&quot;')"/>",</xsl:template>
<xsl:template match="body/supertitle">
  "supertitle": "<xsl:value-of select="string:replace(string:replace(., '&#10;', '\n'), '&quot;', '\&quot;')"/>",</xsl:template>
<xsl:template match="teaser/text">
  "teaser": "<xsl:value-of select="string:replace(string:replace(., '&#10;', '\n'), '&quot;', '\&quot;')"/>",</xsl:template>

<xsl:template mode="body" match="body">
  <!-- Thank you https://stackoverflow.com/a/17098873 -->
  <xsl:for-each select="(//body/division/* | //body/division/ul/*)[(local-name(.) = 'p' or local-name() = 'li' or local-name(.) = 'intertitle') and (translate(normalize-space(.), ' ', '') != '')]">
    { "type": "<xsl:value-of select="name(.)" />", "content": "<xsl:value-of select="string:replace(string:replace(., '&#10;', '\n'), '&quot;', '\&quot;')"/>"}<xsl:if test="position() != last()">,</xsl:if>
    </xsl:for-each>
</xsl:template>

<xsl:template mode="tobool" match="text()[.='yes']">true</xsl:template>
<xsl:template mode="tobool" match="text()[.='no']">false</xsl:template>
</xsl:stylesheet>
