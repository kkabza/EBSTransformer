<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
  
  <!-- Main template -->
  <xsl:template match="/">
    <xsl:text disable-output-escaping="yes">&lt;?xml version="1.0" encoding="UTF-8"?&gt;</xsl:text>
    <Claim>
      <xsl:apply-templates select="/ACORD"/>
    </Claim>
  </xsl:template>
  
  <!-- ACORD template -->
  <xsl:template match="ACORD">
    <Metadata>
      <SystemInfo>
        <Provider>
          <xsl:value-of select="SignonRq/CustId/SPName"/>
        </Provider>
        <ProviderId>
          <xsl:value-of select="SignonRq/CustId/CustPermId"/>
        </ProviderId>
        <SourceSystem>
          <xsl:value-of select="SignonRq/ClientApp/Name"/>
        </SourceSystem>
        <SourceVersion>
          <xsl:value-of select="SignonRq/ClientApp/Version"/>
        </SourceVersion>
      </SystemInfo>
      <RequestId>
        <xsl:value-of select="InsuranceSvcRq/RqUID"/>
      </RequestId>
      <TransactionDate>
        <xsl:value-of select="substring-before(InsuranceSvcRq/PolicyNotificationRq/TransactionRequestDt, 'T')"/>
      </TransactionDate>
      <Currency>
        <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/CurCd"/>
      </Currency>
    </Metadata>
    
    <PolicyInfo>
      <PolicyNumber>
        <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/Policy/PolicyNumber"/>
      </PolicyNumber>
      <LineOfBusiness>
        <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/Policy/LOBCd"/>
      </LineOfBusiness>
      <Agent>
        <AgentId>
          <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/Producer/ProducerInfo/ContractNumber"/>
        </AgentId>
        <AgentRole>
          <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/Producer/ProducerInfo/ProducerRoleCd"/>
        </AgentRole>
        <Name>
          <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/Producer/ProducerInfo/PersonName/FirstName"/>
          <xsl:text> </xsl:text>
          <xsl:value-of select="InsuranceSvcRq/PolicyNotificationRq/Producer/ProducerInfo/PersonName/LastName"/>
        </Name>
      </Agent>
    </PolicyInfo>
    
    <ClaimDetails>
      <xsl:apply-templates select="InsuranceSvcRq/PolicyNotificationRq/ClaimsNotification/ClaimsOccurrence"/>
    </ClaimDetails>
    
    <Parties>
      <xsl:apply-templates select="InsuranceSvcRq/PolicyNotificationRq/ClaimsNotification/ClaimsOccurrence/ClaimsParty"/>
    </Parties>
  </xsl:template>
  
  <!-- ClaimsOccurrence template -->
  <xsl:template match="ClaimsOccurrence">
    <ClaimNumber>
      <xsl:value-of select="ClaimNumber"/>
    </ClaimNumber>
    <OccurrenceDate>
      <xsl:value-of select="substring-before(DateTimeOccurred, 'T')"/>
    </OccurrenceDate>
    <OccurrenceTime>
      <xsl:value-of select="substring-after(DateTimeOccurred, 'T')"/>
    </OccurrenceTime>
    <LossCause>
      <xsl:value-of select="LossCauseCd"/>
    </LossCause>
    <xsl:apply-templates select="ClaimsPayment"/>
  </xsl:template>
  
  <!-- ClaimsPayment template -->
  <xsl:template match="ClaimsPayment">
    <Payment>
      <Amount>
        <xsl:variable name="amount" select="PaymentAmt"/>
        <xsl:choose>
          <xsl:when test="contains($amount, '.')">
            <xsl:value-of select="format-number($amount, '#0.00')"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($amount, '#0.00')"/>
          </xsl:otherwise>
        </xsl:choose>
      </Amount>
      <Coverage>
        <xsl:value-of select="ClaimsPaymentCovInfo/CoverageCd"/>
      </Coverage>
      <Deductible>
        <xsl:variable name="deductible" select="ClaimsPaymentCovInfo/DeductibleAmt"/>
        <xsl:choose>
          <xsl:when test="contains($deductible, '.')">
            <xsl:value-of select="format-number($deductible, '#0.00')"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="format-number($deductible, '#0.00')"/>
          </xsl:otherwise>
        </xsl:choose>
      </Deductible>
    </Payment>
  </xsl:template>
  
  <!-- ClaimsParty template -->
  <xsl:template match="ClaimsParty">
    <Party>
      <Name>
        <xsl:value-of select="ClaimsPartyInfo/PersonName/FirstName"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="ClaimsPartyInfo/PersonName/LastName"/>
      </Name>
      <Role>
        <xsl:value-of select="ClaimsPartyInfo/ClaimsPartyTypeCd"/>
      </Role>
    </Party>
  </xsl:template>
</xsl:stylesheet> 