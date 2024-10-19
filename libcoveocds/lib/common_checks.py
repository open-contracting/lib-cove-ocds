import re


def _update_documents_counter(obj, counter):
    documents = obj.get("documents", [])
    counter.update(document["documentType"] for document in documents if document.get("documentType"))
    return len(documents)


def get_bad_ocid_prefixes(json_data):
    """Yield tuples with ('ocid', 'path/to/ocid') for ocids with malformed prefixes."""
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
        return None

    if records := json_data.get("records"):
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

    if releases := json_data.get("releases"):
        bad_prefixes = []
        if isinstance(releases, list):
            for j, release in enumerate(releases):
                if ocid := _is_bad_prefix(release):
                    bad_prefixes.append((ocid, f"releases/{j}/ocid"))
        return bad_prefixes

    return []
