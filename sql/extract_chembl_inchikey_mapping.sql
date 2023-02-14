SELECT
    DISTINCT `molecule_dictionary`.`chembl_id` AS 'molecule_chembl_id',
    `compound_structures`.`standard_inchi_key`,
    `molecule_dictionary`.`pref_name`
FROM
    `compound_structures`,
    `molecule_dictionary`
WHERE
    `compound_structures`.`molregno` = `molecule_dictionary`.`molregno`
    AND `molecule_dictionary`.`molregno` = `activities`.`molregno`