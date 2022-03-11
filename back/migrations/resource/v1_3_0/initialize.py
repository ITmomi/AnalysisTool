import os
from dao import get_dbinfo
from dao.dao_function import DAOFunction
from dao.dao_base import DAOBaseClass
from service.resources.service_resources import ResourcesService
import psycopg2 as pg2
from config import app_config
import json
import logging

logger = logging.getLogger(app_config.LOG)

APP_VERSION = '1.3.0'


def init_db_v1_3_0():
    config = get_dbinfo()

    with pg2.connect(**config) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"insert into public.analysis_type(type) values('org')")
            cur.execute(f"insert into public.source_type(type) values('multi')")

            sql = '''
            create table if not exists analysis.multi_info
            (
                id             serial  not null
                    constraint multi_info_pk
                        primary key,
                func_id        integer not null
                    constraint multi_info_function_id_fk
                        references analysis.function
                        on update cascade on delete cascade,
                sub_func_id    integer not null
                    constraint multi_info_function_id_fk_2
                        references analysis.function
                        on update cascade on delete cascade,
                source_type    text    not null,
                tab_name       text    not null,
                rid            text    not null
                    constraint multi_info_job_id_fk
                        references cnvset.job
                        on update cascade on delete cascade,
                fid            text,
                db_id          integer,
                table_name     text,
                equipment_name text,
                period_start   text,
                period_end     text,
                sql            text
            );
            
            create unique index if not exists multi_info_id_uindex
                on analysis.multi_info (id);
                
            create table if not exists convert.casp_header
            (
                log_time             timestamp                not null,
                type                 text,
                job_name             text,
                lot_id               text,
                plate_no             text,
                shot_no              text,
                cp                   text,
                glass_id             text,
                mode                 text,
                dir                  text,
                start_psy            text,
                start_msy            text,
                start_smby           text,
                target_psy           text,
                target_msy           text,
                target_smby          text,
                mp_offset            text,
                expo_position_start  text,
                expo_position_finish text,
                valid_tolerance_psy  text,
                valid_tolerance_msy  text,
                valid_tolerance_smby text,
                smb_start_pos        text,
                msy_delay_time       text,
                expo_speed           text,
                smb_speed            text,
                equipment_name       text    default ''::text not null,
                log_idx              integer default 0        not null,
                request_id           varchar(50),
                created_time         timestamp,
                constraint casp_header_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.casp_table
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                cp             text,
                glass_id       text,
                psy            text,
                dr             text,
                my             text,
                yaw            text,
                z              text,
                pitch          text,
                roll           text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint casp_table_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.dr_header
            (
                log_time        timestamp                not null,
                type            text,
                job_name        text,
                lot_id          text,
                plate_no        text,
                shot_no         text,
                cp              text,
                glass_id        text,
                expo_ready_psy  text,
                mpofs           text,
                final_aapsy     text,
                final_aapst     text,
                final_aamsy     text,
                auto_dr         text,
                auto_mr         text,
                final_aavs      text,
                interfero_of_sx text,
                base            text,
                bdc_x           text,
                sdc_dr          text,
                adc_dr          text,
                sdc_yaw         text,
                bdc_yaw         text,
                adc_yaw         text,
                vs_comp         text,
                interferospan   text,
                yaw_dr          text,
                bar_rotate      text,
                mag_tilt_comp   text,
                mag_tilt_diffx  text,
                equipment_name  text    default ''::text not null,
                log_idx         integer default 0        not null,
                request_id      varchar(50),
                created_time    timestamp,
                constraint dr_header_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.dr_table
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                cp             text,
                glass_id       text,
                psy            text,
                comp           text,
                bdc_x          text,
                sdc_dr         text,
                adc_dr         text,
                yaw_dr         text,
                auto_dr        text,
                bar_rotation   text,
                mag_tilt_comp  text,
                mag_tilt_diffx text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint dr_table_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.my_header
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                cp             text,
                glass_id       text,
                expo_ready_psx text,
                expo_ready_psy text,
                final_aapsy    text,
                final_aapst    text,
                final_aamsy    text,
                arc_my         text,
                interfero_ofsy text,
                mp_ofs         text,
                base           text,
                bdc_y          text,
                sdc_my         text,
                adc_my         text,
                sdc_yaw        text,
                bdc_yaw        text,
                adc_yaw        text,
                yaw_my         text,
                mag_x          text,
                mag_y          text,
                magxy_shift    text,
                magyy_shift    text,
                mag_tilt_comp  text,
                mag_tilt_diffy text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint my_header_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.my_table
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                cp             text,
                glass_id       text,
                psy            text,
                comp           text,
                bdc_y          text,
                sdc_my         text,
                adc_my         text,
                yaw_my         text,
                mag_x          text,
                mag_y          text,
                magxy_shift    text,
                magyy_shift    text,
                mag_tilt_comp  text,
                mag_tilt_diffy text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint my_table_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.offset_table
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                glass_id       text,
                pos            text,
                offset_xl      text,
                offset_yl      text,
                offset_xr      text,
                offset_yr      text,
                offset_arc     text,
                xmag_pitch     text,
                xmag_roll      text,
                imag_pitch     text,
                imag_roll      text,
                ymag_pitch     text,
                ymag_roll      text,
                mag_tilt_xl    text,
                mag_tilt_yl    text,
                mag_tilt_xr    text,
                mag_tilt_yr    text,
                mag_tilt_mx    text,
                mag_tilt_arc   text,
                cp             text,
                vs             text,
                mode           text,
                expo_left      text,
                expo_right     text,
                il_mode        text,
                logical_posx   text,
                logical_posy   text,
                logical_post   text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint offset_table_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.yaw_header
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                cp             text,
                glass_id       text,
                expo_ready_psx text,
                expo_ready_psy text,
                expo_ready_msy text,
                base           text,
                sdc_yaw        text,
                adc_yaw        text,
                bdc_t          text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint yaw_header_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.yaw_table
            (
                log_time       timestamp                not null,
                type           text,
                job_name       text,
                lot_id         text,
                plate_no       text,
                shot_no        text,
                cp             text,
                glass_id       text,
                psy            text,
                comp           text,
                sdc_yaw        text,
                adc_yaw        text,
                bdc_t          text,
                equipment_name text    default ''::text not null,
                log_idx        integer default 0        not null,
                request_id     varchar(50),
                created_time   timestamp,
                constraint yaw_table_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create table if not exists convert.machine
            (
                key            text,
                val            text                
            );
            
            create table if not exists convert.adc_measurement
            (
                device              text,
                process             text,
                reserve1st          integer,
                reserve2nd          integer,
                xystep              integer,
                expo_mode           integer,
                adc_mode            integer,
                partial             integer,
                max_step            integer,
                plate               integer,
                step                integer,
                p1_xl               integer,
                p1_yl               integer,
                p1_xr               integer,
                p1_yr               integer,
                p2_xl               integer,
                p2_yl               integer,
                p2_xr               integer,
                p2_yr               integer,
                p3_xl               integer,
                p3_yl               integer,
                p3_xr               integer,
                p3_yr               integer,
                physicalposition_x  integer,
                physicalposition_y  integer,
                physicalpos_theta   integer,
                logicalposition_x   integer,
                logicalposition_y   integer,
                logicalpos_theta    integer,
                p1_measnum          integer,
                p2_measnum          integer,
                p3_measnum          integer,
                baselayermachine_no integer,
                glass_id            text,
                lot_id              text,
                log_time            timestamp                not null,
                chuck               text,
                ami_pos             text,
                cp1                 integer,
                cp2                 integer,
                cp3                 integer,
                vs1                 integer,
                vs2                 integer,
                vs3                 integer,
                dummy_lot_id        text,
                equipment_name      text    default ''::text not null,
                log_idx             integer default 0        not null,
                request_id          varchar(50),
                created_time        timestamp,
                constraint adc_measurement_prog_pkey
                    primary key (equipment_name, log_time, log_idx)
            );
            
            create schema if not exists fab;
            
            create table if not exists fab.fab
            (
                fab_nm       varchar(50) not null
                    constraint fab_pk
                        primary key,
                plate_size_x smallint    not null,
                plate_size_y smallint    not null,
                div_upper    numeric,
                div_lower    numeric
            );
            
            create unique index if not exists fab_fab_nm_uindex
                on fab.fab (fab_nm);
                
            create table if not exists fab.adc_meas_cp_vs_preset
            (
                id     serial      not null
                    constraint adc_meas_cp_vs_preset_pk
                        primary key,
                name   text        not null,
                fab_nm varchar(50) not null
                    constraint adc_meas_cp_vs_preset_fab_fab_nm_fk
                        references fab.fab
                        on update cascade on delete cascade,
                mode   text        not null
            );
            
            create unique index if not exists adc_meas_cp_vs_preset_id_uindex
                on fab.adc_meas_cp_vs_preset (id);
                
            create table if not exists fab.adc_meas_cp_vs_preset_item
            (
                preset_id integer  not null
                    constraint adc_meas_cp_vs_preset_item_adc_meas_cp_vs_preset_id_fk
                        references fab.adc_meas_cp_vs_preset
                        on update cascade on delete cascade,
                shot_no   smallint not null,
                cp1       numeric,
                cp2       numeric,
                cp3       numeric,
                vs1       numeric,
                vs2       numeric,
                vs3       numeric,
                display   varchar(50)
            );
                      
            create table if not exists fab.correction_component_setting
            (
                fab_nm   varchar(50) not null
                    constraint correction_component_setting_fab_fab_nm_fk
                        references fab.fab
                        on update cascade on delete cascade,
                category text        not null,
                setting  text        not null,
                item     text        not null,
                val      boolean     not null
            );

            create table if not exists fab.correction_cp_vs_preset
            (
                id     serial      not null
                    constraint correction_cp_vs_preset_pk
                        primary key,
                name   text        not null,
                fab_nm varchar(50) not null
                    constraint correction_cp_vs_preset_fab_fab_nm_fk
                        references fab.fab
                        on update cascade on delete cascade,
                mode   text        not null
            );
            
            create table if not exists fab.correction_cp_vs_preset_item
            (
                preset_id integer  not null
                    constraint correction_cp_vs_preset_item_correction_cp_vs_preset_id_fk
                        references fab.correction_cp_vs_preset
                        on update cascade on delete cascade,
                shot_no   smallint not null,
                cpmode    varchar(10),
                cp1       numeric,
                cp12d     numeric,
                cp1d      numeric,
                cp21d     numeric,
                cp2       numeric,
                cp23d     numeric,
                cp3d      numeric,
                cp32d     numeric,
                cp3       numeric,
                vsmode    varchar(10),
                vs1l      numeric,
                vs2l      numeric,
                vs3l      numeric,
                vs4l      numeric,
                vsc       numeric,
                vs4r      numeric,
                vs3r      numeric,
                vs2r      numeric,
                vs1r      numeric,
                cp1_chk   boolean,
                cp12d_chk boolean,
                cp1d_chk  boolean,
                cp21d_chk boolean,
                cp2_chk   boolean,
                cp23d_chk boolean,
                cp3d_chk  boolean,
                cp32d_chk boolean,
                cp3_chk   boolean,
                vs1l_chk  boolean,
                vs2l_chk  boolean,
                vs3l_chk  boolean,
                vs4l_chk  boolean,
                vsc_chk   boolean,
                vs4r_chk  boolean,
                vs3r_chk  boolean,
                vs2r_chk  boolean,
                vs1r_chk  boolean
            );
            
            create table if not exists history.history_from_multi
            (
                history_id     integer not null
                    constraint history_from_multi_history_id_fk
                        references history.history
                        on update cascade on delete cascade,
                sub_func_id    integer not null
                    constraint history_from_multi_function_id_fk
                        references analysis.function
                        on update cascade on delete cascade,
                source_type    text    not null,
                tab_name       text    not null,
                rid            text    not null,
                fid            text,
                db_id          integer,
                table_name     text,
                equipment_name text,
                period_start   text,
                period_end     text,
                sql            text
            );
            '''
            cur.execute(sql)

            sql = '''
            delete from cnvbase.convert_error where 1 = 1;
            alter table cnvbase.convert_error add equipment varchar(128);
            alter table cnvbase.convert_error add content varchar(1024);
            alter table cnvbase.convert_rule_item 
            add skip boolean default False not null;
            '''
            cur.execute(sql)

            sql = '''
            alter table analysis.function 
                add system_func bool default false not null;
            '''
            cur.execute(sql)

            cur.execute(f"update settings.information set value='{APP_VERSION}' where key='version'")


def import_rules():
    try:
        path = 'migrations/resource/v1_3_0/data/rules.json'
        with open(path, 'r') as f:
            log_list = json.load(f)

        dao = DAOBaseClass()

        for log in log_list:
            log_define_master = log.pop('log_define_master')
            convert_rule_list = log.pop('convert_rule')

            resp_form = dao.insert(table='cnvbase.log_define_master', data=log_define_master, rtn_id=True)
            if not resp_form.res:
                logger.info(resp_form.msg)
                return

            log_id = resp_form.data

            for convert_rule in convert_rule_list:
                convert_rule_item_list = convert_rule.pop('convert_rule_item')
                resp_form = dao.insert(table='cnvbase.convert_rule', data={**convert_rule, 'log_id': log_id},
                                       rtn_id=True)
                if not resp_form.res:
                    logger.info(resp_form.msg)
                    return

                rule_id = resp_form.data

                for convert_rule_item in convert_rule_item_list:
                    dao.insert(table='cnvbase.convert_rule_item', data={**convert_rule_item, 'rule_id': rule_id})

    except Exception as e:
        logger.info(str(e))


def import_function():
    try:
        path = 'migrations/resource/v1_3_0/data/function_export.json'
        with open(path, 'r', encoding='utf-8') as f:
            func_list = json.load(f)

        dao_func = DAOFunction()
        resources = ResourcesService()

        for function in func_list:
            category = function['category']
            func = function['func']
            convert = function['convert']
            analysis = function['analysis']
            visualization = function['visualization']

            resp_form = dao_func.insert_category_info(category)
            if not resp_form.res:
                logger.info(resp_form.msg)
                return

            category_id = resp_form.data

            resp_form = dao_func.insert_func_info({**func,
                                                   'category_id': category_id,
                                                   'analysis_type': analysis['type']})
            if not resp_form.res:
                logger.info(resp_form.msg)
                return

            func_id = resp_form.data

            if func['source_type'] == 'local':
                resp_form = dao_func.insert_convert_script(convert['script'], func_id=func_id)
                if not resp_form.res:
                    resources.delete_id(func_id=func_id)
                    logger.info(resp_form.msg)
                    return

            resp_form = dao_func.insert_analysis_info(analysis, func_id)
            if not resp_form.res:
                resources.delete_id(func_id=func_id)
                logger.info(resp_form.msg)
                return

            resp_form = dao_func.insert_visual_info(visualization, func_id)
            if not resp_form.res:
                resources.delete_id(func_id=func_id)
                logger.info(resp_form.msg)
                return

        logger.info('function import success')

    except Exception as e:
        logger.info(str(e))
