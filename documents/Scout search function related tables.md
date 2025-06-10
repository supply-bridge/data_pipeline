## Scout By Index

- keyword suggestion auto completion.

After input keyword, then it will call backend to get the possible suppliers or offerings that’s name might match with this key word, then after user select one, it will continue next step.

 

- New search, search type includes both keyword or company, 

| Join table                                                   | Join  connection                                             | Filter field                 | Description |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------- | ----------- |
| Supplier                                                     | .where('supplier.isGroup  = false')   .andWhere('supplier.isPublished = true')  supplier.source  = :source  source_subcategory  supplier.logoFile | Source  Subcategory  Logo    |             |
|                                                              |                                                              |                              |             |
|                                                              |                                                              |                              |             |
|                                                              |                                                              |                              |             |
| SupplierOffering    Offering                                 | If there is  offer id in filter use this clause to filter it. | offeringId                   |             |
| country.regionId  IN (:...globalFootprints)                  | Filter region  id                                            | globalFootprints             |             |
| supplier.countryId  IN (:...operatingLocations)              | Filter  country id                                           | operatingLocations           |             |
| headquarters                                                 | Filter  headquarters                                         | headquarters                 |             |
| sb_supplier_certification                                    |                                                              | certifications               |             |
| sb_supplier_offering                                         | offering                                                     | Offering Ids  or offering Id |             |
| sb_supplier_application                                      |                                                              | applications                 |             |
| sb_supplier_tool                                             |                                                              | tools                        |             |
| sb_oem_partner_supplier                                      |                                                              | oemPartners                  |             |
| sb_oem_partner_supplier  ops  sb_vehicle_brand  vb  sb_vehicle_model  vm | ops.supplier_id  = supplier.id  vb.id =  ops.oem_partner_id  vm.vehicle_brand_id  = vb.id  vm.fuel_type  IN (:...fuelTypes) | fuelTypes                    |             |
| supplier.countryId  IN (:...operatingLocationsCountries)',   |                                                              | operatingLocationsCountries  |             |
| supplier.isTop100  = true                                    |                                                              | Badges.count>0               |             |
| supplier.rating  BETWEEN :ratingFrom AND :ratingTo           |                                                              | ratingFrom  ratingTo         |             |
| supplier.id  IN (:...suppliers)                              |                                                              |                              |             |

 

## Scout By Quick Bridge

After user selects the different offerings on the page, then retrieve suppliers that has the capability. 

The joining statement is same as list above.