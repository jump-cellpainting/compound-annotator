SELECT
    `activities`.`assay_ID` AS 'assay_chembl_id',
    `target_dictionary`.`chembl_id` AS 'target_chembl_id',
    `assays`.`assay_type`,
    `molecule_dictionary`.`chembl_id` AS 'molecule_chembl_id',
    `activities`.`pchembl_value`,
    `assays`.`confidence_score`,
    `compound_structures`.`standard_inchi_key`,
    `molecule_dictionary`.`pref_name`
FROM
    `compound_properties`,
    `compound_structures`,
    `compound_records`,
    `molecule_dictionary`,
    `activities`,
    `assays`,
    `target_dictionary`,
    `target_components`,
    `component_sequences`,
    `source`
WHERE
    `molecule_dictionary`.`molregno` = `compound_records`.`molregno`
    AND `compound_properties`.`molregno` = `molecule_dictionary`.`molregno`
    AND `compound_structures`.`molregno` = `molecule_dictionary`.`molregno`
    AND `molecule_dictionary`.`molregno` = `activities`.`molregno`
    AND `activities`.`assay_ID` = `assays`.`assay_ID`
    AND `assays`.`tid` = `target_dictionary`.`tid`
    AND `target_dictionary`.`tid` = `target_components`.`tid`
    AND `target_components`.`component_id` = `component_sequences`.`component_id`
    AND `activities`.`src_id` = `source`.`src_id`
    AND `activities`.`standard_relation` IN ('=', '==', '===')
    AND `target_dictionary`.`organism` = 'Homo sapiens'
    AND `activities`.`standard_type` IN ('IC50', 'Ki', 'Kd', 'EC50', 'AC50')
    AND `activities`.`pchembl_value` >= 5
    AND `assays`.`confidence_score` >= 5
    AND `assays`.`assay_type` IN ('B', 'F')
    AND `activities`.`potential_duplicate` = 0
    AND `activities`.`data_validity_comment` IS NULL
    AND `molecule_dictionary`.`polymer_flag` = 0
    AND `activities`.`pchembl_value` IS NOT NULL
GROUP BY
    `component_sequences`.`accession`,
    `molecule_dictionary`.`chembl_id`,
    `activities`.`assay_ID`,
    `activities`.`pchembl_value`