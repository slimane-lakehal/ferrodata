with source as (
    select *
    from {{ source('sncf', 'gares') }}
)

select  
  code_uic as uic_code,
  libelle as station_name,
  fret,
  voyageurs as passengers ,
  code_ligne as line_code,
  rg_troncon as track_number,
  pk as kilometer_post,
  commune as city,
  departemen as departement,
  idreseau as network_id,
  x_wgs84 as lon,
  y_wgs84 as lat,
  current_time as _loaded_at
from source
