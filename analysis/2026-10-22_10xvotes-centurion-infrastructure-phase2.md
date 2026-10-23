# 10X Votes / Centurion: Cross-Border Infrastructure Forensics, Phase 2

Prime Rogue Inc. · Analysis dated 2026-10-22 · Revised 2026-10-23 after fact-check (Michigan subscription scope, Calgary event date, asuid note, certificate-dating point) · Data: `data/2026-10-22_10xvotes-azure/`

## Bottom line

The Alberta voter records found on **skcn.10xvotes.com** were served from a Microsoft Azure App Service app in the East US region (Virginia). That app sits in the same Azure subscription as 10X Votes' Wisconsin, Pennsylvania and "hn" apps, and on the same server cluster as its Michigan app. That is a stronger and more specific cross-border finding than Phase 1. It also corrects Phase 1 on several points.

| # | Finding | Confidence |
| --- | --- | --- |
| 1 | skcn.10xvotes.com resolves to `10xvotes-skcn.azurewebsites.net` on Azure stamp `waws-prod-blu-319` (East US), IP 20.119.0.3, the same stamp and IP as mi, wi, pa and hn. | High (live DNS, 2026-10-22) |
| 2 | skcn, wi, pa and hn all carry the identical Azure domain-verification ID (`asuid` TXT `CCE16DBF…D5DFD3`). Azure issues this ID per subscription, so all four apps live in one Azure subscription. | High |
| 3 | skcn ran the same ASP.NET Core codebase as Michigan. Its March 7, 2025 login page loads `MiFamilyVotingWebsite.styles.css` and posts credentials to itself on Azure. | High (Wayback capture) |
| 4 | skcn's certificates were Azure App Service managed certificates (DigiCert/GeoTrust). They were renewed in lockstep with the US-state apps and co-terminated with them. That pattern points to one operator managing one fleet. | High |
| 5 | The jurisdiction apps are DNS-only, not proxied through Cloudflare. Traffic to skcn went straight to Azure. Phase 1's "upload transited Cloudflare's WAF" does not hold for skcn. Cloudflare is the authoritative DNS host for 10xvotes.com. | High for current state; historical proxy state unverified |
| 6 | auth.10xvotes.com is an Auth0 (Okta) custom domain on a US-region tenant, not Vercel. Phase 1's Vercel / Washington D.C. compute argument is withdrawn. | High for current state |
| 7 | The skcn certificate lapsed August 23, 2026 and was never renewed, but its DNS still points to Azure. auth.10xvotes.com was still renewing on September 21, 2026. | High |

What this does not show is where the database itself sat. App Service apps normally use a database in the same region, but that is an inference.

## Scope and method

Everything here is passive and public. Nothing touched 10X Votes or Centurion servers. No accounts were created, no logins attempted, and no voter data was accessed or downloaded.

- **Certificate transparency:** crt.sh, 229 log entries for `%.10xvotes.com` (145 unique certificates after removing precertificate duplicates), plus the Centurion domains.
- **DNS:** Google Public DNS (dns.google) resolutions for A, AAAA, CNAME, NS, MX, TXT, CAA, SOA and Azure `asuid` records, taken 2026-10-22 between about 09:30 and 10:30 UTC.
- **Archives:** Wayback Machine CDX indexes and raw (`id_`) captures for 10xvotes.com and thecenturionproject.ca.
- **Press:** the National Observer's May 20, 2026 report, used to tie skcn to the Alberta records.
- **urlscan.io:** no public scans of 10xvotes.com exist.

Every certificate ID resolves at `https://crt.sh/?id=<id>`, and each Wayback timestamp is a fixed capture URL. Live DNS can change, so re-pull it, with screenshots, before relying on it in a filing.

## Certificate transparency

The CT record confirms Phase 1's host list, finds no hidden hosts, and adds one fact that matters: skcn's certificates were ordered and renewed as part of the same fleet as the US-state apps.

| Host | Certs | First seen | Last issued | Issuer | Reads as |
| --- | --- | --- | --- | --- | --- |
| 10xvotes.com (apex) | 36 | 2024-03-01 | 2026-09-22 | Let's Encrypt, Google Trust | Webflow marketing site |
| www.10xvotes.com | 36 | 2024-03-01 | 2026-09-20 | Let's Encrypt, Google Trust | Webflow marketing site |
| \*.10xvotes.com + apex | 25 | 2024-09-06 | 2026-08-16 | Let's Encrypt, Google Trust (ECDSA) | Cloudflare Universal SSL |
| pay / www.pay | 3 | 2024-03-01 | 2026-01-31 | GoDaddy Secure CA G2 | Payment page, Cloudflare-proxied |
| mi | 6 | 2024-05-24 | 2026-02-23 | GeoTrust (DigiCert) | Azure App Service managed cert |
| hn | 5 | 2024-10-01 | 2026-02-23 | GeoTrust (DigiCert) | Azure App Service managed cert |
| pa | 5 | 2024-10-04 | 2026-02-23 | GeoTrust (DigiCert) | Azure App Service managed cert |
| wi | 5 | 2024-10-17 | 2026-02-23 | GeoTrust (DigiCert) | Azure App Service managed cert |
| **skcn** | 4 | **2025-03-07** | 2026-02-23 | GeoTrust (DigiCert) | Azure App Service managed cert |
| auth | 20 | 2025-04-04 | 2026-09-21 | Let's Encrypt | Auth0 custom domain |

**Fleet renewal pattern.** skcn started on its own cycle: first cert March 7, 2025, then July 25, 2025. Its next cert, issued **December 12, 2025**, expired on **April 14, 2026**, the same day as the mi, wi, pa and hn certs issued January 12, 2026. All five were then issued together on **February 23, 2026** and expired together on **August 23, 2026**. Co-terminating certificates is a deliberate account-level action. It shows skcn being administered as part of the US fleet.

**After August 23, 2026, none of the five jurisdiction hosts got a new certificate.** The apex, www and auth hosts kept renewing through September 2026.

**The certificates also date the direct-to-Azure configuration.** Azure only issues managed certificates to a domain pointing directly at the app, not through a proxy such as Cloudflare (Microsoft support staff: https://learn.microsoft.com/en-us/answers/questions/412809/cant-create-app-service-managed-certificates-while). So skcn pointed straight at Azure on each issuance date: 2025-03-07, 2025-07-25, 2025-12-12 and 2026-02-23. Proxy settings between those dates remain unverified.

**The "GeoTrust" certificates are Azure's, not a separately bought DigiCert account.** Azure App Service managed certificates are issued through DigiCert's GeoTrust intermediates, with six-month validity and midnight start times. That matches these exactly.

The wildcard certificate Phase 1 cited is crt.sh ID 26199793381 (issued 2026-05-09, expiring 2026-08-07). It covers `*.10xvotes.com` at Cloudflare's edge. It is not the certificate skcn presented, because skcn was not proxied.

## DNS and hosting

Every component that touched skcn traffic is a US company, and the compute was in Virginia.

| Host | Resolves to (2026-10-22) | Provider and region |
| --- | --- | --- |
| skcn.10xvotes.com | `10xvotes-skcn.azurewebsites.net` → `waws-prod-blu-319.sip.azurewebsites.windows.net` → `waws-prod-blu-319-7e61.eastus.cloudapp.azure.com` → 20.119.0.3 | Microsoft Azure App Service, East US |
| mi.10xvotes.com | `10xvotes.azurewebsites.net` → same stamp → 20.119.0.3 | Azure, East US |
| wi / pa / hn | `10xvotes-wi` / `-pa` / `-hn.azurewebsites.net` → same stamp → 20.119.0.3 | Azure, East US |
| auth.10xvotes.com | `dev-pozsa82q46m6bv13-cd-…edge.tenants.us.auth0.com` → `auth0-ingress.us.auth0.com.cdn.cloudflare.net` → 172.64.144.74, 104.18.43.182 | Auth0 (Okta), US tenant, fronted by Cloudflare |
| 10xvotes.com, www | 198.202.211.1, `cdn.webflow.com` | Webflow |
| pay.10xvotes.com | 172.67.174.102, 104.21.72.31 | Cloudflare-proxied |
| Nameservers | lisa / andy.ns.cloudflare.com | Cloudflare DNS |
| Mail | aspmx.l.google.com and alternates; SPF includes Google | Google Workspace |
| TXT | two Google site verifications, `brevo-code:…`; DMARC `p=none` | Google, Brevo |

**Azure subscription link.** `asuid.skcn`, `asuid.wi`, `asuid.pa` and `asuid.hn` all return the same custom-domain verification ID, `CCE16DBFD953C667013F67299E71409AE9E7EA7994CD964270E2A5E60AD5DFD3`. Azure issues this ID per subscription. Michigan has no `asuid` record. Azure recommends but does not require the TXT record for a subdomain, so its absence proves nothing either way; Michigan is tied to the fleet by its stamp, its app name and its certificates.

**No other jurisdictions found.** `ab.`, `abcn.` and `ca.10xvotes.com` do not exist (NXDOMAIN). There is no wildcard DNS record. Plausible sibling app names such as `10xvotes-ab`, `-ca`, `-sk`, `-dev` and `-staging` on azurewebsites.net also do not exist. This was a limited check, not an enumeration.

**The Auth0 tenant name starts with "dev-".** That is Auth0's default for auto-created tenants. An observation, not a finding.

**Not checked:** the skcn host was not contacted, so it is unknown whether it still serves anything.

## Archive evidence

- **skcn, 2025-03-07 17:22 UTC:** the same day its first certificate took effect. The root redirected (301) to `/Identity/Account/Login`. That page, titled "Login - 10X Votes", loads `MiFamilyVotingWebsite.styles.css`, the scoped stylesheet ASP.NET Core names after its project, so skcn was built from the Michigan project. The login form posts email and password to itself, on Azure. It also loads LiveChat (livechatinc.com) tracking and DataTables.
- **Shared codebase across states:** pa.10xvotes.com captures from October to December 2024 load the same `MiFamilyVotingWebsite.styles.css` and the same `site.css` version hash (`qBPjS7Wl…`) as Michigan. The search script queries `/voterinfo/setupData` on the server and filters by first name, last name, address, street, city, age range, counties and townships. A "claimed list" view backs the claiming feature.
- **Matches the Observer's account:** registering with an email gave access, and searching one letter of an address returned 1,000 records. About 2,000 Albertans from Red Deer and central Alberta were searchable, and about 150 had been "claimed".
- **auth.10xvotes.com, 2025-04-04:** first capture returned HTTP 426, which fits an Auth0 custom domain. It appeared four weeks after skcn and belongs to a newer app generation, not the per-jurisdiction Identity apps.
- **10X's newer app (January 2026 capture):** the sign-up page, marked "a product of Voteatron", collects SMS consent. The privacy policy captured the same day restricts SMS to US residents and never mentions Canada, cross-border storage, or voter files.

## Centurion-side infrastructure

Centurion's public site is a Wix site with no technical overlap with 10X's Azure stack. The voter app it promoted has not been located in public records.

| Domain | First cert | Hosting | Notes |
| --- | --- | --- | --- |
| thecenturionproject.ca | 2026-02-26 (also `en.` subdomain) | Wix | Confirmed Centurion site |
| centurionproject.ca | 2026-03-18 | Wix | Probably companion or defensive registration; content not checked |
| thecenturionproject.com | 2016-12-01 | cPanel/Google | Predates Centurion by ten years; treat as unrelated |

- **Site build:** Wix Members Area, Events & Tickets, Groups, Forms, Donations, Phone/SMS Campaigns, ShoutOut email marketing, and Facebook Server-Side Events (member and event data is sent to Meta).
- **"My Addresses" is not the voter app.** It is Wix's stock members-area address book.
- **Events:** weekly "Do you want to be a Centurion" sessions from April 16 to July 2, 2026, and "Operation Secure Independence" events in Edmonton (April 29, 2026, where Elections Alberta served Centurion) and Calgary (listed for May 8, 2026, Genesis Centre); both event pages were archived April 26–27. A Wix ticket order for the April 30, 2026 7 p.m. session (order 309B-0J3S-K9V) was completed at about 6:06 p.m. MDT that day, the day of the injunction. That shows registration was still open and processing; it does not by itself show the session was held.
- **No link from the Wix site to any app host** appears in the archived home, resources, donations or event pages.

**Open question:** the production Centurion app, the one Elections Alberta had shut down on April 30, has not been tied to a hostname. Court filings, Elections Alberta's investigation record, or the YouTube training video should name it.

## Timeline

| Date | Event | Source |
| --- | --- | --- |
| 2024-03-01 | pay.10xvotes.com GoDaddy certificate | crt.sh |
| 2024-05-24 | Michigan app on Azure East US (first cert) | crt.sh |
| 2024-10-01 to 10-17 | hn, pa, wi apps added | crt.sh |
| 2025-03-07 | skcn app created, same codebase; archived same day | crt.sh, Wayback |
| 2025-04-04 | auth.10xvotes.com on Auth0 (US) | crt.sh, Wayback |
| 2025-06 | Republican Party of Alberta receives June 2025 electors list | Elections Alberta, in court |
| 2025-12-12 | skcn cert co-terminated with fleet (expiry 2026-04-14) | crt.sh |
| 2026-02-23 | All five jurisdiction apps issued certs together | crt.sh |
| 2026-02-26 | Centurion site (Wix) first cert | crt.sh |
| 2026-04-30 | Injunction; Centurion app offline | Elections Alberta |
| 2026-05-19 | Observer finds skcn; taken offline within hours | National Observer |
| 2026-08-23 | All five jurisdiction certs lapse; none renewed | crt.sh |
| 2026-10-19 | Alberta referendum | — |

## What it proves, and next asks

**Proven from public records.** The host the Observer found holding Alberta voter records (skcn) was a Microsoft Azure web app in Virginia, built from 10X Votes' Michigan code, administered in the same Azure subscription as three US election apps, on the same server cluster as Michigan's, and renewed in lockstep with all four. Login credentials and search queries went straight to that US server.

**Not proven.**

- Where the database lived. Same-region Azure SQL or storage is likely but unseen.
- Whether skcn's ~2,000 records came from the Elections Alberta list. The Observer notes they lacked list identifiers.
- Whether the production Centurion app ran on this subscription.
- Who owns the subscription. Voteatron LLC is the obvious candidate but unconfirmed.

**Corrections to Phase 1.**

1. "Upload transited Cloudflare's US WAF" for skcn is replaced by "skcn was DNS-only; traffic went directly to Microsoft Azure, East US."
2. The Vercel / Washington D.C. compute argument for auth is withdrawn. auth.10xvotes.com is Auth0 (US tenant).
3. "skcn = Saskatchewan" is withdrawn as a finding. The subdomain held Alberta records per the Observer.
4. The "DigiCert/GeoTrust commercial account" is Azure App Service managed certificates. The single-account point stands and is stronger.

**Targets for production orders or an MLAT.**

| Recipient | Ask for | Identifiers |
| --- | --- | --- |
| Microsoft (Azure) | Subscription owner and billing entity; resource group; app and database regions; App Service HTTP and deployment logs; data residency of linked storage | `10xvotes-skcn.azurewebsites.net`, asuid `CCE16DBF…D5DFD3`, stamp `waws-prod-blu-319`, East US |
| Okta (Auth0) | Tenant owner, region, Canadian sign-ups, connected applications | Tenant `dev-pozsa82q46m6bv13`, custom domain auth.10xvotes.com |
| LiveChat (Text Inc.) | Account owner; chat and visitor records from skcn sessions | Script on skcn login page, 2025-03-07 |
| Cloudflare | DNS change history for skcn, including creation and proxy toggles | Zone 10xvotes.com |
| Google Workspace, Brevo | Domain owner; mail sent to Canadian users | 10xvotes.com MX, `brevo-code` TXT |

**Next research steps.**

1. Pull the Court of King's Bench filings and the YouTube training video to identify the production Centurion app's hostname, then run the same DNS and CT workup on it.
2. Obtain one historical passive-DNS lookup for skcn (e.g. SecurityTrails or DomainTools) to confirm it was never Cloudflare-proxied in 2025–2026.
3. Check Michigan LARA filings for Voteatron LLC (agent and officers) to tie the subscription to a legal entity.

## Sources

- crt.sh: https://crt.sh/?q=%25.10xvotes.com and https://crt.sh/?q=%25.thecenturionproject.ca
- Google Public DNS: https://dns.google/ (resolutions of 2026-10-22)
- Wayback CDX: https://web.archive.org/cdx/search/cdx?url=10xvotes.com&matchType=domain&collapse=urlkey
- skcn login capture: https://web.archive.org/web/20250307172251/https://skcn.10xvotes.com/Identity/Account/Login?ReturnUrl=%2F
- National Observer, May 20, 2026: https://www.nationalobserver.com/2026/05/20/investigations/alberta-voter-data-10x-votes-centurion-project
- Elections Alberta, April 30, 2026: https://www.elections.ab.ca/resources/media/news-releases/update-unauthorized-use-of-list-of-electors/
- CBC on the injunction: https://www.cbc.ca/news/canada/edmonton/elections-alberta-electors-database-9.7182667
