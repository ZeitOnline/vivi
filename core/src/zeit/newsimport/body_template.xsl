<?xml version='1.0' encoding="iso-8859-1" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:template match="/">
        <division type="page">
            <xsl:apply-templates/>
        </division>
    </xsl:template>

    <xsl:template match="p">
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match="h2">
        <intertitle>
            <xsl:copy-of select="text()"/>
        </intertitle>
    </xsl:template>

    <xsl:template match="strong">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="em">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="table">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="ol">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="ul">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="a">
        <a>
            <xsl:attribute name="href">
                <xsl:value-of select="./@href"/>
            </xsl:attribute>
            <xsl:value-of select="text()"/>
        </a>
    </xsl:template>

    <xsl:template match="dnl-twitterembed">
        <embed>
            <xsl:attribute name="url">
                <xsl:value-of select="./@src"/>
            </xsl:attribute>
        </embed>
    </xsl:template>
    <xsl:template match="dnl-youtubeembed">
        <embed>
            <xsl:attribute name="url">
                <xsl:value-of select="./@src"/>
            </xsl:attribute>
        </embed>
    </xsl:template>

</xsl:stylesheet>
