<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:zeit="http://www.zeit.de/exslt"
  xmlns:editor="http://www.zeit.de/xml-editor"
  xmlns:xi="http://www.w3.org/2001/XInclude">


  <xsl:attribute-set name="editable">
    <xsl:attribute name="path">
      <xsl:value-of select="zeit:nodepath(.)"/>
    </xsl:attribute>
    <xsl:attribute name="id">
      <xsl:value-of select="generate-id()"/>
    </xsl:attribute>
    <xsl:attribute name="xml-tag-name">
      <xsl:value-of select="name()" />
    </xsl:attribute>
  </xsl:attribute-set>

  
  <xsl:template match="/">
    <xsl:apply-templates select="//body"/>
  </xsl:template>

  <xsl:template match="body">
    <div xsl:use-attribute-sets="editable">
      <xsl:comment>body</xsl:comment>
      <xsl:apply-templates match="./*" />
    </div>
  </xsl:template>

  <xsl:template match="row">
    <div class="row">
      <div xsl:use-attribute-sets="editable">
        <xsl:comment>row</xsl:comment>
        &lt;row&gt;
      </div>
      <xsl:for-each select="./*">
        <div class="row-cell">
          <xsl:comment>row-content</xsl:comment>
          <xsl:apply-templates select="."/>
        </div>
      </xsl:for-each>
    </div>
  </xsl:template>
  
  <xsl:template match="column">
    <div xsl:use-attribute-sets="editable">
      <div class="block-meta">
        Layout: <xsl:value-of select="@layout" />
      </div>
      <xsl:for-each select="block|container">
          <xsl:sort select="@priority" data-type="number"/>
          <xsl:apply-templates select="."/>
      </xsl:for-each>
    </div>
  </xsl:template>


  <xsl:template match="xi:include">
    <div xsl:use-attribute-sets="editable">
      <xsl:comment>include</xsl:comment>
      <xsl:value-of select="@href"/>
    </div>
  </xsl:template>

  <xsl:template match="container">
    <div xsl:use-attribute-sets="editable">
      <div class="block-meta">
        <xsl:comment>Container</xsl:comment>
        <span class="container-id">
          <xsl:value-of select="@id" />
        </span>
        <span class="priority"><xsl:value-of select="@priority" /></span>
      </div> 
      <xsl:apply-templates select="./*" />
    </div>
  </xsl:template>

  <xsl:template match="block">
    <div xsl:use-attribute-sets="editable">
              
      <xsl:choose>
        <xsl:when test="string(@layout)">
            <xsl:attribute name="class">
                block
                <xsl:value-of select="@layout"/>
            </xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
            <xsl:attribute name="class">block</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:attribute name="path">
        <xsl:value-of select="zeit:nodepath(.)"/>
      </xsl:attribute>
 
      <div class="block-meta">
        <xsl:comment>Block</xsl:comment>
        <xsl:value-of select="@href" />
      </div> 

      <xsl:choose>
          <xsl:when test="child::block">
              <!-- this is a block containing more blocks -->
              <xsl:apply-templates select="*[name()!='block']"/>
              <xsl:for-each select="block">
                  <xsl:sort select="@priority" data-type="number"/>
                  <xsl:apply-templates select="."/>
              </xsl:for-each>
           </xsl:when>
          <xsl:otherwise>
              <xsl:apply-templates select="line | feed | ad | raw | title | byline | supertitle | text | image | column"/>
          </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>


  <!--
      Block-Elements
  -->
  <xsl:template match="image">
      <div xsl:use-attribute-sets="editable">
          <img alt="{@alt}" border="{@border}" src="http://zip4.zeit.de/cms_raw/cms/work{@src}">
              <xsl:attribute name="src">
                  <xsl:choose>
                      <xsl:when test="starts-with(@src,'/cms/work')">
                              http://zip4.zeit.de/cms_raw<xsl:value-of select="@src"/>
                      </xsl:when>
                      <xsl:otherwise> http://zip4.zeit.de/cms_raw/cms/work<xsl:value-of select="@src"/>
                      </xsl:otherwise>
                  </xsl:choose>
              </xsl:attribute>
              <xsl:if test="@width">
                  <xsl:attribute name="width">
                      <xsl:value-of select="@width"/>
                  </xsl:attribute>
              </xsl:if>
          </img>
          <xsl:apply-templates select="title|bu|copyright"/>
      </div>
  </xsl:template>

  <xsl:template match="title">
    <p class="teasertitle_mitte" xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates select="a | br | em | image | strong | tt | u | raw | text()"/>
    </p>
  </xsl:template>
  <xsl:template match="supertitle">
    <p class="supertitle" xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates select="a | br | em | image | strong | tt | u | text()"/>
    </p>
  </xsl:template>

  <xsl:template match="subtitle">
    <h2 xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates select="a | br | em | image | strong | tt | u | text()"/>
    </h2>
  </xsl:template>

  <xsl:template match="byline|copyright">
    <em xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates select="a | br | em | image | strong | tt | u | text()"/>
    </em>
    <br/>
  </xsl:template>

  <xsl:template match="line">
    <div xsl:use-attribute-sets="editable">
      <xsl:comment>line</xsl:comment>
    </div>
  </xsl:template>

  <xsl:template match="feed"/>

  <xsl:template match="ad"/>

  <xsl:template match="node()|@*" mode="copy">
      <xsl:copy>
          <xsl:apply-templates select="node()|@*" mode="copy"/>
      </xsl:copy>
  </xsl:template>
  <xsl:template match="raw">
    <span xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates mode="copy"/>
    </span>
  </xsl:template>

  <xsl:template match="text|bu">
      <span class="teasertext" xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
        <xsl:apply-templates select="text()|a|br|em|image|strong|tt|u|raw|span"/>
      </span>
  </xsl:template>
  <!-- 
      Inline-Elements
  -->
  <xsl:template match="a">
    <a xsl:use-attribute-sets="editable">
      <xsl:copy-of select="@*"/>
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates/>
    </a>
  </xsl:template>
  <xsl:template match="em">
    <em xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates/>
    </em>
  </xsl:template>
  <xsl:template match="strong|span">
    <strong xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates/>
    </strong>
  </xsl:template>
  <xsl:template match="br">
    <br xsl:use-attribute-sets="editable"/>
  </xsl:template>
  <xsl:template match="tt">
    <tt xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates/>
  </tt>
  </xsl:template>
  <xsl:template match="u">
    <u xsl:use-attribute-sets="editable">
      <xsl:comment>not-empty</xsl:comment>
      <xsl:apply-templates/>
    </u>
  </xsl:template>
</xsl:stylesheet>
