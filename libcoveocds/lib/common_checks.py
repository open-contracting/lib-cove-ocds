import collections
import re

import libcove.lib.tools as tools


@tools.ignore_errors
def get_releases_aggregates(json_data):
    release_count = 0
    unique_ocids = set()
    tags = collections.Counter()
    unique_lang = set()
    unique_initation_type = set()
    unique_release_ids = set()
    duplicate_release_ids = set()

    #  for matching with contracts
    unique_award_id = set()

    planning_ocids = set()
    tender_ocids = set()
    awardid_ocids = set()
    award_ocids = set()
    contractid_ocids = set()
    contract_ocids = set()
    implementation_contractid_ocids = set()
    implementation_ocids = set()

    release_dates = []
    tender_dates = []
    award_dates = []
    contract_dates = []

    unique_buyers_identifier = {}
    unique_buyers_name_no_id = set()
    unique_suppliers_identifier = {}
    unique_suppliers_name_no_id = set()
    unique_procuring_identifier = {}
    unique_procuring_name_no_id = set()
    unique_tenderers_identifier = {}
    unique_tenderers_name_no_id = set()

    unique_organisation_schemes = set()
    organisation_identifier_address = set()
    organisation_name_no_id_address = set()
    organisation_identifier_contact_point = set()
    organisation_name_no_id_contact_point = set()

    release_tender_item_ids = set()
    release_award_item_ids = set()
    release_contract_item_ids = set()
    item_identifier_schemes = set()
    unique_item_ids = set()

    unique_currency = set()

    planning_doctype = collections.Counter()
    planning_doc_count = 0
    tender_doctype = collections.Counter()
    tender_doc_count = 0
    tender_milestones_doctype = collections.Counter()
    tender_milestones_doc_count = 0
    award_doctype = collections.Counter()
    award_doc_count = 0
    contract_doctype = collections.Counter()
    contract_doc_count = 0
    implementation_doctype = collections.Counter()
    implementation_doc_count = 0
    implementation_milestones_doctype = collections.Counter()
    implementation_milestones_doc_count = 0

    def process_org(org, unique_id, unique_name):
        if not isinstance(org, dict):
            return

        identifier = org.get("identifier")
        org_id = None
        if identifier:
            org_id = identifier.get("id")
            if org_id:
                unique_id[org_id] = org.get("name", "") or ""
                scheme = identifier.get("scheme")
                if scheme:
                    unique_organisation_schemes.add(scheme)
                if org.get("address"):
                    organisation_identifier_address.add(org_id)
                if org.get("contactPoint"):
                    organisation_identifier_contact_point.add(org_id)
        if not org_id:
            name = org.get("name")
            if name:
                unique_name.add(name)
            if org.get("address"):
                organisation_name_no_id_address.add(name)
            if org.get("contactPoint"):
                organisation_name_no_id_contact_point.add(name)

    def get_item_scheme(item):
        classification = item.get("classification")
        if classification:
            scheme = classification.get("scheme")
            if scheme:
                item_identifier_schemes.add(scheme)

    releases = tools.get_no_exception(json_data, "releases", [])
    for release in releases:
        # ### Release Section ###
        release_count = release_count + 1
        ocid = release.get("ocid")
        release_id = release.get("id")
        if not ocid:
            continue
        if release_id:
            if release_id in unique_release_ids:
                duplicate_release_ids.add(release_id)
            unique_release_ids.add(release_id)

        unique_ocids.add(release["ocid"])
        if "tag" in release:
            tags.update(tools.to_list(release["tag"]))
        initiation_type = release.get("initiationType")
        if initiation_type:
            unique_initation_type.add(initiation_type)

        release_date = release.get("date", "")
        if release_date:
            release_dates.append(str(release_date))

        if "language" in release:
            unique_lang.add(release["language"])
        buyer = release.get("buyer")
        if buyer:
            process_org(buyer, unique_buyers_identifier, unique_buyers_name_no_id)

        # ### Planning Section ###
        planning = tools.get_no_exception(release, "planning", {})
        if planning and isinstance(planning, dict):
            planning_ocids.add(ocid)
            planning_doc_count += tools.update_docs(planning, planning_doctype)

        # ### Tender Section ###
        tender = tools.get_no_exception(release, "tender", {})
        if tender and isinstance(tender, dict):
            tender_ocids.add(ocid)
            tender_doc_count += tools.update_docs(tender, tender_doctype)
            tender_period = tender.get("tenderPeriod")
            if tender_period:
                start_date = tender_period.get("startDate", "")
                if start_date:
                    tender_dates.append(str(start_date))
            procuring_entity = tender.get("procuringEntity")
            if procuring_entity:
                process_org(procuring_entity, unique_procuring_identifier, unique_procuring_name_no_id)
            tenderers = tender.get("tenderers", [])
            for tenderer in tenderers:
                process_org(tenderer, unique_tenderers_identifier, unique_tenderers_name_no_id)
            tender_items = tender.get("items", [])
            for item in tender_items:
                item_id = item.get("id")
                if item_id:
                    unique_item_ids.add(item_id)
                if item_id and release_id:
                    release_tender_item_ids.add((ocid, release_id, item_id))
                get_item_scheme(item)
            milestones = tender.get("milestones")
            if milestones:
                for milestone in milestones:
                    tender_milestones_doc_count += tools.update_docs(milestone, tender_milestones_doctype)

        # ### Award Section ###
        awards = tools.get_no_exception(release, "awards", [])
        for award in awards:
            if not isinstance(award, dict):
                continue
            award_id = award.get("id")
            award_ocids.add(ocid)
            if award_id:
                unique_award_id.add(award_id)
                awardid_ocids.add((award_id, ocid))
            award_date = award.get("date", "")
            if award_date:
                award_dates.append(str(award_date))
            award_items = award.get("items", [])
            for item in award_items:
                item_id = item.get("id")
                if item_id:
                    unique_item_ids.add(item_id)
                if item_id and release_id and award_id:
                    release_award_item_ids.add((ocid, release_id, award_id, item_id))
                get_item_scheme(item)
            suppliers = award.get("suppliers", [])
            for supplier in suppliers:
                process_org(supplier, unique_suppliers_identifier, unique_suppliers_name_no_id)
            award_doc_count += tools.update_docs(award, award_doctype)

        # ### Contract section
        contracts = tools.get_no_exception(release, "contracts", [])
        for contract in contracts:
            contract_id = contract.get("id")
            contract_ocids.add(ocid)
            if contract_id:
                contractid_ocids.add((contract_id, ocid))
            period = contract.get("period")
            if period:
                start_date = period.get("startDate", "")
                if start_date:
                    contract_dates.append(start_date)
            contract_items = contract.get("items", [])
            for item in contract_items:
                item_id = item.get("id")
                if item_id:
                    unique_item_ids.add(item_id)
                if item_id and release_id and contract_id:
                    release_contract_item_ids.add((ocid, release_id, contract_id, item_id))
                get_item_scheme(item)
            contract_doc_count += tools.update_docs(contract, contract_doctype)
            implementation = contract.get("implementation")
            if implementation:
                implementation_ocids.add(ocid)
                if contract_id:
                    implementation_contractid_ocids.add((contract_id, ocid))
                implementation_doc_count += tools.update_docs(implementation, implementation_doctype)
                implementation_milestones = implementation.get("milestones", [])
                for milestone in implementation_milestones:
                    implementation_milestones_doc_count += tools.update_docs(
                        milestone, implementation_milestones_doctype
                    )

    contracts_without_awards = []
    for release in releases:
        contracts = release.get("contracts", [])
        for contract in contracts:
            award_id = contract.get("awardID")
            if award_id not in unique_award_id:
                contracts_without_awards.append(contract)

    unique_buyers_count = len(unique_buyers_identifier) + len(unique_buyers_name_no_id)
    unique_buyers = [name + " (" + str(id) + ")" for id, name in unique_buyers_identifier.items()] + list(
        unique_buyers_name_no_id
    )

    unique_suppliers_count = len(unique_suppliers_identifier) + len(unique_suppliers_name_no_id)
    unique_suppliers = [name + " (" + str(id) + ")" for id, name in unique_suppliers_identifier.items()] + list(
        unique_suppliers_name_no_id
    )

    unique_procuring_count = len(unique_procuring_identifier) + len(unique_procuring_name_no_id)
    unique_procuring = [name + " (" + str(id) + ")" for id, name in unique_procuring_identifier.items()] + list(
        unique_procuring_name_no_id
    )

    unique_tenderers_count = len(unique_tenderers_identifier) + len(unique_tenderers_name_no_id)
    unique_tenderers = [name + " (" + str(id) + ")" for id, name in unique_tenderers_identifier.items()] + list(
        unique_tenderers_name_no_id
    )

    unique_org_identifier_count = len(
        set(unique_buyers_identifier)
        | set(unique_suppliers_identifier)
        | set(unique_procuring_identifier)
        | set(unique_tenderers_identifier)
    )
    unique_org_name_count = len(
        unique_buyers_name_no_id
        | unique_suppliers_name_no_id
        | unique_procuring_name_no_id
        | unique_tenderers_name_no_id
    )
    unique_org_count = unique_org_identifier_count + unique_org_name_count

    def get_currencies(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "currency":
                    if isinstance(value, list):
                        for versioned_value in value:
                            if "value" in versioned_value:
                                unique_currency.add(versioned_value["value"])
                    else:
                        unique_currency.add(value)
                get_currencies(value)
        if isinstance(obj, list):
            for item in obj:
                get_currencies(item)

    get_currencies(json_data)

    return {
        "release_count": release_count,
        "unique_ocids": sorted(unique_ocids, key=lambda x: str(x)),
        "unique_initation_type": sorted(unique_initation_type, key=lambda x: str(x)),
        "duplicate_release_ids": sorted(duplicate_release_ids, key=lambda x: str(x)),
        "tags": dict(tags),
        "unique_lang": sorted(unique_lang, key=lambda x: str(x)),
        "unique_award_id": sorted(unique_award_id, key=lambda x: str(x)),
        "planning_count": len(planning_ocids),
        "tender_count": len(tender_ocids),
        "award_count": len(awardid_ocids),
        "processes_award_count": len(award_ocids),
        "contract_count": len(contractid_ocids),
        "processes_contract_count": len(contract_ocids),
        "implementation_count": len(implementation_contractid_ocids),
        "processes_implementation_count": len(implementation_ocids),
        "min_release_date": min(release_dates) if release_dates else "",
        "max_release_date": max(release_dates) if release_dates else "",
        "min_tender_date": min(tender_dates) if tender_dates else "",
        "max_tender_date": max(tender_dates) if tender_dates else "",
        "min_award_date": min(award_dates) if award_dates else "",
        "max_award_date": max(award_dates) if award_dates else "",
        "min_contract_date": min(contract_dates) if contract_dates else "",
        "max_contract_date": max(contract_dates) if contract_dates else "",
        "unique_buyers_identifier": unique_buyers_identifier,
        "unique_buyers_name_no_id": sorted(unique_buyers_name_no_id, key=lambda x: str(x)),
        "unique_suppliers_identifier": unique_suppliers_identifier,
        "unique_suppliers_name_no_id": sorted(unique_suppliers_name_no_id, key=lambda x: str(x)),
        "unique_procuring_identifier": unique_procuring_identifier,
        "unique_procuring_name_no_id": sorted(unique_procuring_name_no_id, key=lambda x: str(x)),
        "unique_tenderers_identifier": unique_tenderers_identifier,
        "unique_tenderers_name_no_id": sorted(unique_tenderers_name_no_id, key=lambda x: str(x)),
        "unique_buyers": sorted(set(unique_buyers)),
        "unique_suppliers": sorted(set(unique_suppliers)),
        "unique_procuring": sorted(set(unique_procuring)),
        "unique_tenderers": sorted(set(unique_tenderers)),
        "unique_buyers_count": unique_buyers_count,
        "unique_suppliers_count": unique_suppliers_count,
        "unique_procuring_count": unique_procuring_count,
        "unique_tenderers_count": unique_tenderers_count,
        "unique_org_identifier_count": unique_org_identifier_count,
        "unique_org_name_count": unique_org_name_count,
        "unique_org_count": unique_org_count,
        "unique_organisation_schemes": sorted(unique_organisation_schemes, key=lambda x: str(x)),
        "organisations_with_address": len(organisation_identifier_address) + len(organisation_name_no_id_address),
        "organisations_with_contact_point": len(organisation_identifier_contact_point)
        + len(organisation_name_no_id_contact_point),
        "total_item_count": len(release_tender_item_ids)
        + len(release_award_item_ids)
        + len(release_contract_item_ids),
        "tender_item_count": len(release_tender_item_ids),
        "award_item_count": len(release_award_item_ids),
        "contract_item_count": len(release_contract_item_ids),
        "unique_item_ids_count": len(unique_item_ids),
        "item_identifier_schemes": sorted(item_identifier_schemes, key=lambda x: str(x)),
        "unique_currency": sorted(unique_currency, key=lambda x: str(x)),
        "planning_doc_count": planning_doc_count,
        "tender_doc_count": tender_doc_count,
        "tender_milestones_doc_count": tender_milestones_doc_count,
        "award_doc_count": award_doc_count,
        "contract_doc_count": contract_doc_count,
        "implementation_doc_count": implementation_doc_count,
        "implementation_milestones_doc_count": implementation_milestones_doc_count,
        "planning_doctype": dict(planning_doctype),
        "tender_doctype": dict(tender_doctype),
        "tender_milestones_doctype": dict(tender_milestones_doctype),
        "award_doctype": dict(award_doctype),
        "contract_doctype": dict(contract_doctype),
        "implementation_doctype": dict(implementation_doctype),
        "implementation_milestones_doctype": dict(implementation_milestones_doctype),
        "contracts_without_awards": contracts_without_awards,
    }


@tools.ignore_errors
def get_records_aggregates(json_data):
    # Unique ocids
    unique_ocids = set()

    if "records" in json_data:
        for record in json_data["records"]:
            # Gather all the ocids
            if "ocid" in record:
                unique_ocids.add(record["ocid"])

    # Number of records
    count = len(json_data["records"]) if "records" in json_data else 0

    return {
        "count": count,
        "unique_ocids": unique_ocids,
    }


def get_bad_ocid_prefixes(json_data):
    """Yield tuples with ('ocid', 'path/to/ocid') for ocids with malformed prefixes"""
    if not isinstance(json_data, dict):
        return []

    prefix_regex = re.compile(r"^ocds-[a-z0-9]{6}")

    def _is_bad_prefix(item):
        if (
            isinstance(item, dict)
            and (ocid := item.get("ocid"))
            and isinstance(ocid, str)
            and not prefix_regex.match(ocid)
        ):
            return ocid

    records = json_data.get("records")
    if records:
        bad_prefixes = []
        if isinstance(records, list):
            for i, record in enumerate(records):
                if not isinstance(record, dict):
                    continue

                if ocid := _is_bad_prefix(record):
                    bad_prefixes.append((ocid, f"records/{i}/ocid"))

                releases = record.get("releases")
                if isinstance(releases, list):
                    for j, release in enumerate(releases):
                        if ocid := _is_bad_prefix(release):
                            bad_prefixes.append((ocid, f"records/{i}/releases/{j}/ocid"))

                compiled_release = record.get("compiledRelease")
                if ocid := _is_bad_prefix(compiled_release):
                    bad_prefixes.append((ocid, f"records/{i}/compiledRelease/ocid"))
        return bad_prefixes

    releases = json_data.get("releases")
    if releases:
        bad_prefixes = []
        if isinstance(releases, list):
            for j, release in enumerate(releases):
                if ocid := _is_bad_prefix(release):
                    bad_prefixes.append((ocid, f"releases/{j}/ocid"))
        return bad_prefixes

    return []
