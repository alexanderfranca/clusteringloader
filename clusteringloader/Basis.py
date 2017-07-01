from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

protein_ecs   = Table(
                     'protein_ecs',
                     Base.metadata,
                     Column('protein_id', Integer, ForeignKey('proteins.id')),
                     Column('ec_id', Integer, ForeignKey('ecs.id')),
                   )

protein_maps  = Table(
                     'protein_maps',
                     Base.metadata,
                     Column('protein_id', Integer, ForeignKey('proteins.id')),
                     Column('map_id', Integer, ForeignKey('pathway_maps.id')),
                   )


ec_maps       = Table(
                     'ec_maps',
                     Base.metadata,
                     Column('ec_id', Integer, ForeignKey('ecs.id')),
                     Column('map_id', Integer, ForeignKey('pathway_maps.id')),
                   )

organism_ecs  = Table(
                     'organism_ecs',
                     Base.metadata,
                     Column('organism_id', Integer, ForeignKey('organisms.id')),
                     Column('ec_id', Integer, ForeignKey('ecs.id')),
                   )

organism_maps = Table(
                     'organism_maps',
                     Base.metadata,
                     Column('organism_id', Integer, ForeignKey('organisms.id')),
                     Column('map_id', Integer, ForeignKey('pathway_maps.id')),
                   )

organism_taxonomies = Table(
                     'organism_taxonomies',
                     Base.metadata,
                     Column('organism_id', Integer, ForeignKey('organisms.id')),
                     Column('taxonomy_id', Integer, ForeignKey('taxonomies.id')),
                   )


