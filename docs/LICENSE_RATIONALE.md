# License Rationale

This document objectively outlines the implications of sticking with the current AGPL-3.0 license versus switching to a more permissive license (like MIT or Apache-2.0) for the Gabriel project.

## GNU Affero General Public License v3.0 (AGPL-3.0)
*Currently applied*

- **Implications for Users**: Anyone can use the tool for free. However, if they modify Gabriel and offer it as a service over a network (e.g., hosting Gabriel as a multi-user web service), they **must** release their modified source code under AGPL.
- **Commercial Use**: Allowed, but the strong copyleft nature often deters large enterprises from incorporating the code into their proprietary SaaS platforms.
- **Contributor Threshold**: Higher. Developers from corporate environments may face legal hurdles contributing to or adopting AGPL projects.
- **Protection**: Ensures that any improvements made to Gabriel, even if only exposed via a web interface, remain open-source.

## MIT / Apache-2.0 (Permissive)

- **Implications for Users**: Anyone can use, modify, distribute, and even sell the software with very few restrictions (primarily requiring preservation of copyright and license notices).
- **Commercial Use**: Highly attractive to enterprises. Companies can fork Gabriel, modify it, integrate it into a paid proprietary product, and they do not have to share their source code.
- **Contributor Threshold**: Lower. The permissive nature encourages widespread adoption and contributions from developers in all environments.
- **Protection**: Offers no guarantee that downstream modifications will be contributed back to the open-source community. Apache-2.0 additionally provides an explicit grant of patent rights, which is beneficial for corporate adoption.

### Summary
- Choose **AGPL-3.0** if the priority is protecting the codebase from being closed-sourced by others who offer it as a service.
- Choose **MIT/Apache-2.0** if the priority is maximizing adoption, integrations, and community contributions, with the tradeoff that others can monetize modified versions without sharing their code.
