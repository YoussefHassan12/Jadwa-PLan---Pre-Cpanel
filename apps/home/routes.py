# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024
"""

from flask import render_template, request, session, redirect, url_for,flash,jsonify
from apps.home import blueprint
from apps.config import config
from jinja2 import TemplateNotFound
from functools import wraps
import os, psycopg2
import shutil
from werkzeug.utils import secure_filename
import json


OPENAI_API_KEY = "sk-proj-VwTYgACukwJ7Erp5unKIT3BlbkFJwClnWksCSVGV7qdYmPoE"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('username'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('authentication_blueprint.login'))

    return wrap


def get_bplan_list():
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        # sql = """
        #       SELECT b.bplan_id, \
        #              b.name, \
        #              b.email, \
        #              b.industry, \
        #              b.buz_sector, \
        #              b.buz_subsector, \
        #              b.buz_currency, \
        #              b.creation_date, \
        #              b.status, \
        #              b.completion, \
        #              e.client_avatar
        #       FROM public.bplan b
        #                LEFT JOIN public.buz_export_plan e ON b.bplan_id = e.bplan_id
        #       ORDER BY b.creation_date DESC; \
        #       """
        # cur.execute(sql)
        user_id = session.get('user_id')  # NEW

        sql = """
        SELECT b.bplan_id, b.name, b.email, b.industry, b.buz_sector, 
               b.buz_subsector, b.buz_currency, b.creation_date, 
               b.status, b.completion, e.client_avatar
        FROM public.bplan b
        LEFT JOIN public.buz_export_plan e ON b.bplan_id = e.bplan_id
        WHERE b.user_id = %s
        ORDER BY b.creation_date DESC;
        """
        cur.execute(sql, (user_id,))

        rows = cur.fetchall()

        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append(result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def get_bplan(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT bplan_id, name, email, industry, buz_sector, buz_subsector, buz_currency, creation_date, status, completion, \
                complete_client_profile, complete_business_profile, complete_business_premises, complete_market_analysis, complete_competitors, \
                complete_operations_plan, complete_requested_fund, complete_feasibility FROM public.bplan WHERE bplan_id = {} AND user_id = {};".format(bplan_id,session.get('user_id'))
        cur.execute(sql)
        rows = cur.fetchall()

        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)


        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

# def insert_bplan(var_name, var_industry, var_sector, var_subsector, var_currency, var_status,var_objective_type, var_objective_target, var_objective_timeline, var_objective_unit,var_objective_strategy):
#
#     # Check if the 'bplan_inserted' session flag is already set
#     if 'bplan_inserted' in session and session['bplan_inserted']:
#         print("Data already inserted for this session.")
#         return "Data already inserted for this session."
#
#     conn = None
#     try:
#         db_params = config()
#         conn = psycopg2.connect(**db_params)
#         cur = conn.cursor()
#         var_email = session.get('username')
#         var_user_id = session.get('user_id')  # NEW
#
#         sql = "INSERT INTO public.bplan(Name, Email, industry, buz_sector, buz_subsector, buz_currency, Creation_date, Status, Completion, complete_client_profile, complete_business_profile, complete_business_premises, complete_market_analysis, complete_competitors, complete_operations_plan, complete_requested_fund, complete_feasibility, user_id, Objective_Type, Objective_Target, Objective_Timeline, Objective_Unit, Objective_Strategy) " \
#               " VALUES ('{}','{}','{}','{}','{}','{}',current_timestamp,'{}',0, '0', '0', '0', '0', '0', '0', '0', '0', {}, '{}', {}, {}, '{}', '{}')".format(
#             var_name, var_email, var_industry, var_sector, var_subsector, var_currency, var_status, var_user_id,
#             var_objective_type, var_objective_target, var_objective_timeline, var_objective_unit,
#             # Added quotes around this
#             var_objective_strategy)
#         cur.execute(sql)
#
#         sql = "SELECT MAX(bplan_id) FROM public.bplan"
#         cur.execute(sql)
#         bplan_id = cur.fetchall()
#
#         sql = "INSERT INTO public.client_info(bplan_id, full_name, client_avatar, gender, marital_status, number_of_children, nationality, dob, education_level, years_of_experience, education_major, specialty, education_institution) " \
#               " VALUES ({}, '', 'avatar.png', 1, 1, 0, 1, to_date('2000-01-01','YYYY-MM-DD'), 1, 0, '', '', '');".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.employed(bplan_id, emp_where, emp_job_hold, emp_location, emp_duration, emp_monthly_income) " \
#               " VALUES ({}, '', '', '', '', 0);".format(bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.side_business(bplan_id, buz_name, buz_industry, buz_location, buz_duration, buz_monthly_income) " \
#               "VALUES ({}, '', 1, '', '', 0);".format(bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_info(bplan_id, buz_name, buz_address, buz_est_date, buz_legal_status, buz_model, product_services) " \
#               "VALUES ({}, '{}', '', to_date('2000-01-01','YYYY-MM-DD'), NULL, '[1]', NULL);".format(bplan_id[0][0], var_name)
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_mkt_analysis (bplan_id, segment_name, business_model, segment_percentage, market_channel, age_min, age_max, income_min, income_max, male_rate, female_rate, education, occupation, life_stage, location, preferences, industry, company_size) VALUES ({}, '', 'B2B', 0, '[]', 20, 80, 500, 8000, 49, 51, '[]', '[]', '[]', '', '', '', '');".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_preferences (SELECT {}, preference_id, category_id, preference, 0, 0, 0, 0, 0, 0,false from public.lst_preferences);".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_competitor(bplan_id, competitor_name_1st, competitor_name_2nd, competitor_name_3rd) VALUES ({}, '', '', '');".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_operation_plan(bplan_id, enhance_production, customer_support) VALUES ({}, '[]', '[]');".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_feasibility(bplan_id, first_year, second_year, third_year, fourth_year, fifth_year, annual_growth, inflation_rate, depreciation) VALUES ({}, 0, 0, 0, 0, 0, 0, 0, 0);".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_fund_details( bplan_id, project_objectives, project_purposes, fund_type, amount, equity, interest_rate, period, grace_period) VALUES ({}, '[]', '[]', '', 0, 0, 0, 0, 0);".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         sql = "INSERT INTO public.buz_export_plan(bplan_id, client_avatar, full_name, client_gender, client_profile, client_experiences, client_partners, client_expenses, client_employed, side_business, business_profile, buz_staff , buz_resource, business_premises, market_analysis, buz_suppliers, buz_production, enhance_production, buz_distribution, customer_support, requested_fund, feasibility)	\
#         VALUES ({}, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');".format(
#             bplan_id[0][0])
#         cur.execute(sql)
#
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#         return ("*", error)
#     finally:
#         if conn is not None:
#             conn.commit()
#             conn.close()
#     return "Insertion successful"

def insert_bplan_with_objectives(var_name, var_industry, var_sector, var_subsector,
                                 var_currency, var_status, objectives):
    """
    Insert a new business plan with multiple objectives support.

    Args:
        var_name: Brand name
        var_industry: Industry ID
        var_sector: Sector name
        var_subsector: Sub-sector name (optional)
        var_currency: Currency code
        var_status: Project status
        objectives: List of objective dictionaries with keys:
                   - type: Objective type
                   - strategy: Strategy
                   - target: Target percentage (optional)
                   - timeline: Timeline number (optional)
                   - unit: Time unit (optional)

    Returns:
        str: Success message or error tuple
    """

    # Check if the 'bplan_inserted' session flag is already set
    if 'bplan_inserted' in session and session['bplan_inserted']:
        print("Data already inserted for this session.")
        return "Data already inserted for this session."

    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        var_email = session.get('username')
        var_user_id = session.get('user_id')

        # Extract primary objective (first one) for backward compatibility
        primary_objective = objectives[0] if objectives else {}
        var_objective_type = primary_objective.get('type', '')
        var_objective_target = primary_objective.get('target') or 0
        var_objective_timeline = primary_objective.get('timeline') or 0
        var_objective_unit = primary_objective.get('unit', '')
        var_objective_strategy = primary_objective.get('strategy', '')

        # Insert main bplan record with parameterized query (safer)
        sql = """
            INSERT INTO public.bplan(
                Name, Email, industry, buz_sector, buz_subsector, buz_currency, 
                Creation_date, Status, Completion, 
                complete_client_profile, complete_business_profile, complete_business_premises, 
                complete_market_analysis, complete_competitors, complete_operations_plan, 
                complete_requested_fund, complete_feasibility, user_id, 
                Objective_Type, Objective_Target, Objective_Timeline, Objective_Unit, Objective_Strategy
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                current_timestamp, %s, 0, 
                '0', '0', '0', '0', '0', '0', '0', '0', %s, 
                %s, %s, %s, %s, %s
            ) RETURNING bplan_id
        """

        cur.execute(sql, (
            var_name, var_email, var_industry, var_sector, var_subsector, var_currency,
            var_status, var_user_id,
            var_objective_type, var_objective_target, var_objective_timeline,
            var_objective_unit, var_objective_strategy
        ))

        bplan_id = cur.fetchone()[0]

        # Insert all objectives into the new bplan_objectives table
        if objectives:
            for idx, obj in enumerate(objectives):
                sql_objective = """
                    INSERT INTO public.bplan_objectives(
                        bplan_id, objective_order, objective_type, objective_strategy,
                        objective_target, objective_timeline, objective_unit
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql_objective, (
                    bplan_id,
                    idx + 1,  # objective_order (1-based)
                    obj.get('type', ''),
                    obj.get('strategy', ''),
                    obj.get('target') or None,
                    obj.get('timeline') or None,
                    obj.get('unit', '')
                ))

        # Insert client_info
        sql = """
            INSERT INTO public.client_info(
                bplan_id, full_name, client_avatar, gender, marital_status, 
                number_of_children, nationality, dob, education_level, 
                years_of_experience, education_major, specialty, education_institution
            ) VALUES (%s, '', 'avatar.png', 1, 1, 0, 1, '2000-01-01', 1, 0, '', '', '')
        """
        cur.execute(sql, (bplan_id,))

        # Insert employed
        sql = """
            INSERT INTO public.employed(
                bplan_id, emp_where, emp_job_hold, emp_location, emp_duration, emp_monthly_income
            ) VALUES (%s, '', '', '', '', 0)
        """
        cur.execute(sql, (bplan_id,))

        # Insert side_business
        sql = """
            INSERT INTO public.side_business(
                bplan_id, buz_name, buz_industry, buz_location, buz_duration, buz_monthly_income
            ) VALUES (%s, '', 1, '', '', 0)
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_info
        sql = """
            INSERT INTO public.buz_info(
                bplan_id, buz_name, buz_address, buz_est_date, buz_legal_status, buz_model, product_services
            ) VALUES (%s, %s, '', '2000-01-01', NULL, '[1]', NULL)
        """
        cur.execute(sql, (bplan_id, var_name))

        # Insert buz_mkt_analysis
        sql = """
            INSERT INTO public.buz_mkt_analysis(
                bplan_id, segment_name, business_model, segment_percentage, market_channel,
                age_min, age_max, income_min, income_max, male_rate, female_rate,
                education, occupation, life_stage, location, preferences, industry, company_size
            ) VALUES (%s, '', 'B2B', 0, '[]', 20, 80, 500, 8000, 49, 51, '[]', '[]', '[]', '', '', '', '')
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_preferences
        sql = """
            INSERT INTO public.buz_preferences 
            SELECT %s, preference_id, category_id, preference, 0, 0, 0, 0, 0, 0, false 
            FROM public.lst_preferences
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_competitor
        sql = """
            INSERT INTO public.buz_competitor(
                bplan_id, competitor_name_1st, competitor_name_2nd, competitor_name_3rd
            ) VALUES (%s, '', '', '')
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_operation_plan
        sql = """
            INSERT INTO public.buz_operation_plan(
                bplan_id, enhance_production, customer_support
            ) VALUES (%s, '[]', '[]')
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_feasibility
        sql = """
            INSERT INTO public.buz_feasibility(
                bplan_id, first_year, second_year, third_year, fourth_year, fifth_year,
                annual_growth, inflation_rate, depreciation
            ) VALUES (%s, 0, 0, 0, 0, 0, 0, 0, 0)
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_fund_details
        sql = """
            INSERT INTO public.buz_fund_details(
                bplan_id, project_objectives, project_purposes, fund_type, amount,
                equity, interest_rate, period, grace_period
            ) VALUES (%s, '[]', '[]', '', 0, 0, 0, 0, 0)
        """
        cur.execute(sql, (bplan_id,))

        # Insert buz_export_plan
        sql = """
            INSERT INTO public.buz_export_plan(
                bplan_id, client_avatar, full_name, client_gender, client_profile,
                client_experiences, client_partners, client_expenses, client_employed,
                side_business, business_profile, buz_staff, buz_resource, business_premises,
                market_analysis, buz_suppliers, buz_production, enhance_production,
                buz_distribution, customer_support, requested_fund, feasibility
            ) VALUES (%s, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
        """
        cur.execute(sql, (bplan_id,))

        conn.commit()
        cur.close()

        return "Insertion successful"

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        if conn:
            conn.rollback()
        return ("*", str(error))
    finally:
        if conn is not None:
            conn.close()


def get_bplan_objectives(bplan_id):
    """
    Retrieve all objectives for a business plan.

    Args:
        bplan_id: Business plan ID

    Returns:
        list: List of objective dictionaries
    """
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            SELECT objective_id, objective_order, objective_type, objective_strategy,
                   objective_target, objective_timeline, objective_unit
            FROM public.bplan_objectives
            WHERE bplan_id = %s
            ORDER BY objective_order
        """
        cur.execute(sql, (bplan_id,))
        rows = cur.fetchall()

        objectives = []
        for row in rows:
            objectives.append({
                'id': row[0],
                'order': row[1],
                'type': row[2],
                'strategy': row[3],
                'target': row[4],
                'timeline': row[5],
                'unit': row[6]
            })

        cur.close()
        return objectives

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()


def update_bplan_objectives(bplan_id, objectives):
    """
    Update objectives for a business plan (delete existing and insert new).

    Args:
        bplan_id: Business plan ID
        objectives: List of objective dictionaries

    Returns:
        bool: Success status
    """
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Delete existing objectives
        sql = "DELETE FROM public.bplan_objectives WHERE bplan_id = %s"
        cur.execute(sql, (bplan_id,))

        # Insert new objectives
        for idx, obj in enumerate(objectives):
            sql = """
                INSERT INTO public.bplan_objectives(
                    bplan_id, objective_order, objective_type, objective_strategy,
                    objective_target, objective_timeline, objective_unit
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                bplan_id,
                idx + 1,
                obj.get('type', ''),
                obj.get('strategy', ''),
                obj.get('target') or None,
                obj.get('timeline') or None,
                obj.get('unit', '')
            ))

        # Update primary objective in bplan table for backward compatibility
        if objectives:
            primary = objectives[0]
            sql = """
                UPDATE public.bplan 
                SET Objective_Type = %s, Objective_Target = %s, 
                    Objective_Timeline = %s, Objective_Unit = %s, Objective_Strategy = %s
                WHERE bplan_id = %s
            """
            cur.execute(sql, (
                primary.get('type', ''),
                primary.get('target') or 0,
                primary.get('timeline') or 0,
                primary.get('unit', ''),
                primary.get('strategy', ''),
                bplan_id
            ))

        conn.commit()
        cur.close()
        return True

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn is not None:
            conn.close()



def delete_bplan_db(bplan_id):
    """
    Delete business plan and all related data from database tables
    """
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Verify the bplan belongs to the current user
        var_user_id = session.get('user_id')
        cur.execute("SELECT bplan_id FROM public.bplan WHERE bplan_id = %s AND user_id = %s",
                   (bplan_id, var_user_id))
        bplan_exists = cur.fetchone()

        if not bplan_exists:
            return False, "Business plan not found or you don't have permission to delete it."

        # Delete from all related tables
        tables_to_delete = [
            'buz_competitor',
            'buz_distribution',
            'buz_expenses',
            'buz_export_plan',
            'buz_feasibility',
            'buz_feasibility_operating_expenses',
            'buz_financial_history',
            'buz_fund_details',
            'buz_fund_items',
            'buz_info',
            'buz_mkt_analysis',
            'buz_operation_plan',
            'buz_oresource',
            'buz_other_resource',
            'buz_preferences',
            'buz_premise',
            'buz_premises_doc',
            'buz_premises_photo',
            'buz_product_services',
            'buz_production',
            'buz_products',
            'buz_resource',
            'buz_staff',
            'buz_supplier',
            'buz_suppliers',
            'buz_suppliers_products_info',
            'buz_yearly_commission',
            'client_info',
            'employed',
            'expenses',
            'experiences',
            'partners',
            'side_business'
        ]

        records_deleted = 0
        for table in tables_to_delete:
            try:
                sql = f"DELETE FROM public.{table} WHERE bplan_id = %s"
                cur.execute(sql, (bplan_id,))
                records_deleted += cur.rowcount
                print(f"✅ Deleted from {table} where bplan_id = {bplan_id}")
            except Exception as e:
                print(f"❌ Error deleting from {table}: {e}")

        # Finally delete the main bplan record
        sql = "DELETE FROM public.bplan WHERE bplan_id = %s"
        cur.execute(sql, (bplan_id,))
        records_deleted += cur.rowcount

        cur.close()
        conn.commit()

        return True, f"Deleted {records_deleted} records from database"

    except Exception as error:
        print(f"❌ Database error: {error}")
        return False, f"Database error: {error}"
    finally:
        if conn is not None:
            conn.close()

def diagnose_uploads_structure(bplan_id):
    """
    Check what files and directories actually exist for a bplan_id
    """
    print(f"🔍 Diagnosing uploads structure for bplan_id: {bplan_id}")

    # Check all possible paths
    paths_to_check = [
        f"apps/static/uploads/{bplan_id}",
        f"static/uploads/{bplan_id}",
        f"uploads/{bplan_id}",
        f"apps/static/uploads/",  # Check if files are directly here
        f"static/uploads/",
        f"uploads/"
    ]

    for path in paths_to_check:
        if os.path.exists(path):
            print(f"📁 Found: {path}")
            if os.path.isdir(path):
                # List all files in directory
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        print(f"   📄 {file_path}")
            else:
                print(f"   (is a file, not directory)")
        else:
            print(f"❌ Not found: {path}")

def delete_bplan_files(bplan_id):
    """
    Delete all uploaded files and photos for a business plan from filesystem
    """
    try:
        files_deleted = 0

        # First, let's diagnose the actual structure
        diagnose_uploads_structure(bplan_id)

        # Try multiple possible directory structures
        directories_to_remove = [
            # Your current structure
            f"apps/static/uploads/{bplan_id}",
            f"apps/static/uploads/docs/{bplan_id}",
            f"apps/static/uploads/docs/temp/{bplan_id}",

            # Alternative structures
            f"static/uploads/{bplan_id}",
            f"uploads/{bplan_id}",
            f"../uploads/{bplan_id}",

            # Also check for files directly in uploads (not in bplan_id subfolder)
            f"apps/static/uploads/",  # We'll handle this differently
            f"static/uploads/",
            f"uploads/"
        ]

        for directory in directories_to_remove:
            try:
                if os.path.exists(directory) and os.path.isdir(directory):
                    # Special handling for root uploads directories
                    if directory in ["apps/static/uploads/", "static/uploads/", "uploads/"]:
                        # Look for files that belong to this bplan_id
                        for filename in os.listdir(directory):
                            file_path = os.path.join(directory, filename)
                            if os.path.isfile(file_path):
                                # Check if filename contains bplan_id or other logic
                                if str(bplan_id) in filename:
                                    os.remove(file_path)
                                    files_deleted += 1
                                    print(f"✅ Deleted file: {file_path}")
                    else:
                        # Normal directory deletion
                        file_count = sum(len(files) for _, _, files in os.walk(directory))
                        shutil.rmtree(directory)
                        files_deleted += file_count
                        print(f"✅ Deleted directory: {directory} ({file_count} files)")

            except Exception as e:
                print(f"❌ Error deleting {directory}: {e}")


        print(f"📊 Total files deleted: {files_deleted}")
        return files_deleted

    except Exception as e:
        print(f"❌ Error in delete_bplan_files: {e}")
        return

def delete_bplan_complete(bplan_id):
    """
    Complete deletion of business plan - both database records and filesystem files
    """
    try:
        # Step 1: Delete from database
        db_success, db_message = delete_bplan_db(bplan_id)

        if not db_success:
            return db_message  # Return the error message

        # Step 2: Delete files from filesystem
        files_deleted = delete_bplan_files(bplan_id)

        # Step 3: Clear session flags
        if 'current_bplan_id' in session and session['current_bplan_id'] == bplan_id:
            session.pop('current_bplan_id', None)
            session.pop('bplan_inserted', None)

        # Bilingual success message
        if session.get('lang', 'en') == 'ar':
            return f"تم حذف خطة العمل بنجاح و {files_deleted} ملف مرفوع"
        else:
            return f"Business plan deleted successfully and {files_deleted} uploaded files removed"

    except Exception as error:
        print(f"❌ Complete deletion error: {error}")
        if session.get('lang', 'en') == 'ar':
            return f"خطأ في حذف خطة العمل: {error}"
        else:
            return f"Error deleting business plan: {error}"

def get_lst_industries():
    
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.lst_industries order by 1;"
        cur.execute(sql)
        rows = cur.fetchall()
            
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def get_lst_sectors():
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.lst_sectors ORDER BY 1;"
        cur.execute(sql)
        rows = cur.fetchall()
            
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_bplan_completion ( var_section, bplan_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.bplan SET {} = True WHERE bplan_id={};".format(var_section, bplan_id)
        cur.execute(sql)
        
        sql = "UPDATE public.bplan SET completion = \
                (COALESCE((CASE WHEN complete_client_profile THEN 15 END),0) + COALESCE((CASE WHEN complete_business_profile THEN 15 END),0) \
                + COALESCE((CASE WHEN complete_business_premises THEN 10 END),0) + COALESCE((CASE WHEN complete_market_analysis THEN 15 END),0) \
                + COALESCE((CASE WHEN complete_competitors THEN 10 END),0) + COALESCE((CASE WHEN complete_operations_plan THEN 15 END),0) \
                + COALESCE((CASE WHEN complete_requested_fund THEN 10 END),0) + COALESCE((CASE WHEN complete_feasibility THEN 10 END),0)) \
                WHERE bplan_id={}" .format( bplan_id)
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_completion(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT completion FROM public.bplan where bplan_id = {};".format(bplan_id)
        cur.execute(sql)
        rows = cur.fetchall()
            
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

# Client Profile
def get_client_profile(bplan_id):
    
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.client_info where bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        rows = cur.fetchall()
            
        # if len(rows) == 0 :
        #     results = [{"bplan_id": bplan_id, 
        #             "full_name": '', 
        #             "gender": 1, 
        #             "marital_status": 1, 
        #             "number_of_children": 0, 
        #             "nationality": 1, 
        #             "dob": datetime.datetime.strptime('01-01-2000', '%d-%m-%Y'), 
        #             "education_level": 1, 
        #             "years_of_experience": 0, 
        #             "education_major": '', 
        #             "specialty": '', 
        #             "education_institution": ''}]
        #     sql = "INSERT INTO public.client_info(bplan_id, full_name, gender, marital_status, number_of_children, nationality, dob, education_level, years_of_experience, education_major, specialty, education_institution) " \
	    #         " VALUES ({}, '', 1, 1, 0, 1, to_date('2000-01-01','YYYY-MM-DD'), 1, 0, '', '', '');".format(bplan_id)
        #     cur.execute(sql)
        #     conn.commit()
        # else:
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def get_lst_nationalities():
    
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.lst_nationalities ;"
        cur.execute(sql)
        rows = cur.fetchall()
            
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_client_profile(full_name, client_avatar, gender,marital_status,number_of_children,nationality, dob,education_level, years_of_experience, education_major,specialty, education_institution, bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if number_of_children in ('',None): number_of_children = 0

        sql = "UPDATE public.client_info SET full_name='{}', client_avatar='{}', gender='{}', marital_status='{}', number_of_children={}, nationality='{}', dob='{}', education_level='{}', years_of_experience={}, education_major='{}', specialty='{}', education_institution='{}' WHERE bplan_id ={};".format(full_name,client_avatar, gender,marital_status,number_of_children,nationality, dob,education_level, years_of_experience, education_major,specialty, education_institution, bplan_id)
        cur.execute(sql)

        sql = "UPDATE public.buz_export_plan SET client_avatar='{}', full_name='{}', client_gender='{}' WHERE bplan_id ={};".format(client_avatar, full_name, gender, bplan_id)
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_partners(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.partners where bplan_id ={} order by partner_id;".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def partner_delete(partner_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.partners where partner_id = {};".format(partner_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def partner_add(bplan_id, partner_name, choice_partner_relation, partner_experience, partner_years_of_experience, partner_role, partner_shares):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if partner_years_of_experience in ('',None): partner_years_of_experience = 0

        sql = "INSERT INTO public.partners( bplan_id, partner_name, partner_relation, partner_experience, partner_years_of_experience, partner_role, partner_shares) \
        VALUES ({}, '{}', '{}', '{}', {}, '{}', {});".format(bplan_id, partner_name, choice_partner_relation,  partner_experience, partner_years_of_experience, partner_role, partner_shares)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def experience_delete(experience_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.experiences where experience_id = {};".format(experience_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_experiences(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.experiences where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def experiences_add(bplan_id, experience_field, years_of_experience, experience_workplace):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if years_of_experience in ('',None):
            years_of_experience = 0
         
        sql = "INSERT INTO public.experiences( bplan_id, field, years_of_experience, workplace) VALUES ({}, '{}', {}, '{}');".format(bplan_id, experience_field, years_of_experience, experience_workplace)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_expenses(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.expenses WHERE bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        sql = "SELECT sum(total_value) as total_value FROM public.expenses WHERE bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        total_result = cur.fetchall()
        if total_result[0][0] == None: total_value = 0
        else: total_value = total_result[0][0]

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error, None)
    finally:
        if conn is not None:
            conn.close()
    return (True, results, total_value)


def expenses_add(bplan_id, expense_name, expense_value, expense_unit):
    conn = None
    try:
        # ✅ DEBUG: Print what we received
        print("=" * 80)
        print("EXPENSES_ADD CALLED")
        print(f"bplan_id: {bplan_id} (type: {type(bplan_id)})")
        print(f"expense_name: '{expense_name}' (type: {type(expense_name)})")
        print(f"expense_value: '{expense_value}' (type: {type(expense_value)})")
        print(f"expense_unit: '{expense_unit}' (type: {type(expense_unit)})")
        print("=" * 80)

        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Convert expense_value to integer, default to 0 if empty/None
        if expense_value in ('', None):
            expense_value = 0
        else:
            expense_value = int(expense_value)

        # Calculate total based on unit
        if expense_unit == '2':  # Monthly
            expense_total = expense_value * 12
        else:  # Yearly
            expense_total = expense_value

        # ✅ DEBUG: Print what we're about to insert
        print(f"INSERTING INTO DB:")
        print(f"  living_expenses: '{expense_name}'")
        print(f"  value: {expense_value}")
        print(f"  unit: {expense_unit}")
        print(f"  total_value: {expense_total}")

        # Use parameterized query
        sql = """
            INSERT INTO public.expenses(bplan_id, living_expenses, value, unit, total_value) 
            VALUES (%s, %s, %s, %s, %s);
        """
        cur.execute(sql, (bplan_id, expense_name, expense_value, expense_unit, expense_total))

        print("✅ INSERT SUCCESSFUL")
        print("=" * 80)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("❌ ERROR in expenses_add:")
        print(error)
        print("=" * 80)
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def client_profile_expense_delete(expense_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.expenses where expense_id = {};".format(expense_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_employed(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.employed where bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        rows = cur.fetchall()
            
        # if len(rows) == 0 :
        #     results = [{"bplan_id": bplan_id, 
        #             "emp_where": '', 
        #             "emp_job_hold": '', 
        #             "emp_location": '', 
        #             "emp_duration": '', 
        #             "emp_monthly_income": 0}]
            
        #     sql = "INSERT INTO public.employed(bplan_id, emp_where, emp_job_hold, emp_location, emp_duration, emp_monthly_income) " \
	    #         " VALUES ({}, '', '', '', '', 0);".format(bplan_id)
        #     cur.execute(sql)
        #     conn.commit()
        # else:
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_employed (employed_where,employed_job_hold,employed_location, employed_duration, employed_monthly_income, bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.employed SET emp_where='{}', emp_job_hold='{}', emp_location='{}', emp_duration='{}', emp_monthly_income={} WHERE bplan_id ={};".format(employed_where,employed_job_hold,employed_location,employed_duration,employed_monthly_income, bplan_id)
        cur.execute(sql)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return
    
def get_side_business(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.side_business where bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        rows = cur.fetchall()
         
        # if len(rows) == 0 :
        #     results = [{"bplan_id": bplan_id, 
        #             "buz_name": '', 
        #             "buz_industry": '', 
        #             "buz_location": '', 
        #             "buz_duration": '', 
        #             "buz_monthly_income": 0}]
            
        #     sql = "INSERT INTO public.side_business(bplan_id, buz_name, buz_industry, buz_location, buz_duration, buz_monthly_income) " \
        #             	"VALUES ({}, '', '', '', '', 0);".format(bplan_id)
        #     cur.execute(sql)
        #     conn.commit()
        # else:
        columns = [column[0] for column in cur.description]
        results = []

        for row in rows:
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_side_business (business_name,business_industry,business_location,business_duration,business_monthly_income,bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.side_business SET buz_name='{}', buz_industry={}, buz_location='{}', buz_duration='{}', buz_monthly_income={} WHERE bplan_id ={};".format(business_name,business_industry,business_location,business_duration,business_monthly_income, bplan_id)
        cur.execute(sql)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

# Business Profile
def get_buz_info(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_info where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_info ( buz_address, buz_est_date, buz_legal_status, buz_model, product_services, bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if buz_legal_status in ('',None): buz_legal_status = 0

        sql = "UPDATE public.buz_info SET buz_address='{}', buz_est_date='{}', buz_legal_status={}, buz_model='{}', product_services='{}' \
            WHERE bplan_id ={};".format( buz_address, buz_est_date, buz_legal_status, buz_model, product_services, bplan_id)
        print(sql)

        cur.execute(sql)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

# Youssef product and services:
def product_service_add(bplan_id, name, description, image):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
        INSERT INTO public.buz_product_services
        (bplan_id, product_service_name, product_service_description, product_service_image)
        VALUES (%s, %s, %s, %s);
        """
        cur.execute(sql, (bplan_id, name, description, image))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def update_product_service(service_id, name=None, description=None, image=None):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        updates = []
        if name is not None:
            updates.append(f"product_service_name = '{name}'")
        if description is not None:
            updates.append(f"product_service_description = '{description}'")
        if image is not None:
            updates.append(f"product_service_image = '{image}'")

        if updates:
            sql = f"""
            UPDATE public.buz_product_services
            SET {', '.join(updates)}
            WHERE product_service_id = {service_id};
            """
            cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_product_services(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT * FROM public.buz_product_services WHERE bplan_id = %s;"
        cur.execute(sql, (bplan_id,))
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error, None)
    finally:
        if conn is not None:
            conn.close()
    return (True, results)

def delete_product_service(service_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "DELETE FROM public.buz_product_services WHERE product_service_id = %s;"
        cur.execute(sql, (service_id,))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

########################################################################################


def staff_add(bplan_id, staff_position, choice_work_time, staff_salary):
    conn = None
    try:       
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if staff_salary in ('',None): staff_salary = 0
        
        sql = "INSERT INTO public.buz_staff( bplan_id, staff_position, work_time, staff_salary, total_salary) VALUES ({}, '{}', '{}', {}, {});".format(bplan_id, staff_position, choice_work_time, staff_salary, int(staff_salary)*12)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def staff_delete(staff_id):
    conn = None
    try:    
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_staff where staff_id = {};".format(staff_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_staff(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_staff where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []
        total = 0

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            # total += result['staff_salary']
            results.append (result)

        sql = "SELECT sum(total_salary) as total_salary FROM public.buz_staff WHERE bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        total_result = cur.fetchall()
        if total_result[0][0] == None: total_salary = 0
        else: total_salary = total_result[0][0]

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error , None)
    finally:
        if conn is not None:
            conn.close()
    return (True, results, total_salary)

def resource_add(bplan_id, resource_type, resource_subtype, resource_value ):
    conn = None
    try:      
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if resource_value in ('',None): resource_value = 0
        
        sql = "INSERT INTO public.buz_resource( bplan_id, resource_type, resource_subtype, resource_value, depreciation) VALUES ({}, '{}', '{}', {}, 0);".format(bplan_id, resource_type, resource_subtype, resource_value)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def update_buz_resource(resource_id, depreciation):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_resource SET depreciation={} WHERE resource_id={} ;".format(depreciation, resource_id)
        cur.execute(sql)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_resource(bplan_id):
    conn = None
    try:   
        db_params = config()    
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_resource where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        sql = "SELECT sum(resource_value) as total_value FROM public.buz_resource WHERE bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        total_result = cur.fetchall()
        if total_result[0][0] == None: total_value = 0
        else: total_value = total_result[0][0]

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error, None )
    finally:
        if conn is not None:
            conn.close()
    return (True, results, total_value)

def resource_delete(resource_id):
    conn = None
    try:
        db_params = config()      
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_resource where resource_id = {};".format(resource_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def financial_add(bplan_id, financial_year, financial_sales, financial_profit ):
    conn = None
    try:      
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if financial_sales in ('',None): financial_sales = 0
        if financial_profit in ('',None): financial_profit = 0
        
        sql = "INSERT INTO public.buz_financial_history(bplan_id, financial_year, financial_sales, financial_profit) VALUES ({}, '{}', {}, {});".format(bplan_id, financial_year, financial_sales, financial_profit)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def financial_delete(financial_id):
    conn = None
    print('in the function financial_delete')
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_financial_history where financial_id = {};".format(financial_id)
        print(sql)
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return


def get_buz_financial(bplan_id):
    conn = None
    try:   
        db_params = config()    
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_financial_history where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def get_buz_other_resource(bplan_id):
    conn = None
    try:
        db_params = config()      
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_other_resource where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def other_resource_add(bplan_id, choice_fund, fund_contribution ):
    conn = None
    try:
        db_params = config()      
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if fund_contribution in ('',None): fund_contribution = 0
        
        sql = "INSERT INTO public.buz_other_resource ( bplan_id, funds, contribution) VALUES ({}, '{}', {});".format(bplan_id, choice_fund, fund_contribution)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def other_resource_delete(other_resource_id):
    conn = None
    try:
        db_params = config()       
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_other_resource where other_resource_id = {};".format(other_resource_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

# Business Premises
def premise_add(bplan_id, premise_address, plot_number, premise_nature, plot_area, premise_ownership, premise_surrounding, partner_name, partner_relation, percentage_of_ownership, rent_fees, rent_period, rent_unit):
    conn = None
    try:
        db_params = config()      
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if plot_area in ('',None): plot_area = 0
        if percentage_of_ownership in ('',None): percentage_of_ownership = 0
        if rent_fees in ('',None): rent_fees = 0
        if rent_period in ('',None): rent_period = 0

        sql = "INSERT INTO public.buz_premise(bplan_id, premise_address, plot_number, premise_nature, plot_area, \
            premise_ownership, premise_surrounding, partner_name, partner_relation, percentage_of_ownership, rent_fees, \
            rent_period, rent_unit ) VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {}, '{}')" \
            .format(bplan_id,premise_address, plot_number, premise_nature, plot_area, premise_ownership, premise_surrounding, partner_name, partner_relation, percentage_of_ownership, rent_fees, rent_period, rent_unit)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_premise(bplan_id):
    conn = None
    try:
        db_params = config()       
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_premise where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def premise_delete(premise_id):
    conn = None
    try: 
        db_params = config()      
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_premise where premise_id = {};".format(premise_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_premises_photo(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT * from public.buz_premises_photo where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")


def get_buz_premises_doc(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # FIXED: Use parameterized query to prevent SQL injection
        sql = "SELECT * FROM public.buz_premises_doc WHERE bplan_id = %s;"
        cur.execute(sql, (bplan_id,))

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append(result)

        cur.close()
        return (results, "")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching business premises documents: {error}")
        return ([], str(error))  # Return empty list on error
    finally:
        if conn is not None:
            conn.close()

def premises_photo_add(bplan_id, filename, description=None):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """INSERT INTO public.buz_premises_photo (bplan_id, premises_photo_filename, description) 
                 VALUES (%s, %s, %s)"""
        cur.execute(sql, (bplan_id, filename, description))
        conn.commit()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return ("", "")

def premises_photo_delete(photo_id):
    conn = None
    try: 
        db_params = config()      
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Use parameterized query instead of string formatting
        cur.execute("DELETE FROM public.buz_premises_photo WHERE photo_id = %s", (photo_id,))

        conn.commit()  # Move commit before closing cursor
        cur.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()  # Rollback on error
        print("Error deleting photo:", error)
        return False
    finally:
        if conn is not None:
            conn.close()

def premises_doc_delete(doc_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # First get the filename and bplan_id to delete the physical file
        cur.execute("SELECT bplan_id, premises_doc_filename FROM buz_premises_doc WHERE doc_id = %s", (doc_id,))
        result = cur.fetchone()

        if result:
            bplan_id, filename = result
            # Delete physical file
            file_path = f"apps/static/uploads/docs/{bplan_id}/{filename}"
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete database record
            cur.execute("DELETE FROM buz_premises_doc WHERE doc_id = %s", (doc_id,))

        conn.commit()
        cur.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error deleting document:", error)
        return False
    finally:
        if conn is not None:
            conn.close()

# Market Analysis
def get_preferences(bplan_id, category_id, preference_value_check):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if category_id != "":
            var_category = " and bp.category_id = {}".format(category_id)
        else:
            var_category = ""

        if preference_value_check:
            var_preference = " and bp.preference_value > 0"
        else:
            var_preference = ""

        sql = """
            SELECT 
                bp.*,
                lp.preference_ar
            FROM public.buz_preferences bp
            LEFT JOIN public.lst_preferences lp ON bp.preference = lp.preference
            WHERE bp.bplan_id = {} 
            {} 
            {} 
            ORDER BY bp.preference;
        """.format(bplan_id, var_category, var_preference)

        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append(result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.close()
    return (results, "")


def get_selected_preferences_only(bplan_id, preference_value_check=False):
    """
    Get only the selected preferences (is_selected=True) for a business plan
    Similar to get_preferences but always filters by is_selected=True
    """
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Base query for selected preferences only
        sql = """
            SELECT 
                bp.*,
                lp.preference_ar
            FROM public.buz_preferences bp
            LEFT JOIN public.lst_preferences lp ON bp.preference = lp.preference
            WHERE bp.bplan_id = %s 
            AND bp.is_selected = TRUE
        """

        params = [bplan_id]

        # Handle preference_value condition
        if preference_value_check:
            sql += " AND bp.preference_value > 0"

        # Add ORDER BY
        sql += " ORDER BY bp.preference;"

        # print(f"Executing get_selected_preferences_only SQL: {sql}")  # Debug print
        # print(f"With params: {params}")  # Debug print

        cur.execute(sql, params)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append(result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_preferences( bplan_id ,preference, preference_value):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_preferences SET preference_value={} WHERE bplan_id={} and preference='{}' ;".format(preference_value, bplan_id, preference)
        cur.execute(sql)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_mkt_channels():
    conn = None
    try:  
        db_params = config()     
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.lst_mkt_channels"
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "") 

def get_buz_mkt_segments(bplan_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT segment_id, segment_name, segment_percentage FROM public.buz_mkt_analysis WHERE bplan_id = {} ORDER BY 1;".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def buz_mkt_segments_delete(segment_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_mkt_analysis where segment_id = {};".format(segment_id)
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return


def add_buz_mkt_segments (bplan_id):
    conn = None
    try:     
        db_params = config()  
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "INSERT INTO public.buz_mkt_analysis (bplan_id, segment_name, business_model, segment_percentage, market_channel, age_min, age_max, income_min, income_max, male_rate, female_rate, education, occupation, life_stage, location, preferences, industry, company_size) VALUES ({}, '<name>', 'B2B', 0, '[]', 20, 80, 500, 8000, 49, 51, '[]', '[]', '[]', '', '', '', '');".format(bplan_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_last_mkt_segments(bplan_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT max(segment_id) FROM public.buz_mkt_analysis WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)
        rows = cur.fetchall()
        
        last_segment_id = rows[0][0]

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (last_segment_id)

def get_buz_mkt_analysis(bplan_id, segment_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_mkt_analysis WHERE bplan_id = {} and segment_id = {};".format(bplan_id, segment_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "") 

def update_buz_mkt_analysis( segment_name, business_model, segment_percentage, market_channel, age_min, age_max, income_min, income_max, male_rate, female_rate, education, occupation, life_stage, b2c_location, b2b_location, preferences, industry, company_size,show_age_range,show_income_range ,show_gender_percentage ,show_education ,show_occupation ,show_life_stage,bplan_id, segment_id ):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if segment_percentage in ('',None): segment_percentage = 0
        if age_min in ('',None): age_min = 20
        if age_max in ('',None): age_max = 80
        if income_min in ('',None): income_min = 500
        if income_max in ('',None): income_max = 8000
        if male_rate in ('',None): male_rate = 49
        if female_rate in ('',None): female_rate = 51
        if business_model == "B2C": location = b2c_location
        if business_model == "B2B": location = b2b_location
        print(business_model, location)

        sql = """
                UPDATE public.buz_mkt_analysis
                SET segment_name='{}',
                    business_model='{}',
                    segment_percentage={},
                    market_channel='{}',
                    age_min={},
                    age_max={},
                    income_min={},
                    income_max={},
                    male_rate={},
                    female_rate={},
                    education='{}',
                    occupation='{}',
                    life_stage='{}',
                    location='{}',
                    preferences='{}',
                    industry='{}',
                    company_size='{}',
                    show_age_range='{}',show_income_range='{}' ,show_gender_percentage='{}' ,show_education='{}' ,show_occupation='{}' ,show_life_stage='{}'
                WHERE bplan_id={} AND segment_id={};
                """.format(segment_name, business_model, segment_percentage, market_channel, age_min, age_max, income_min, income_max,
                           male_rate, female_rate, education, occupation, life_stage, location, preferences, industry, company_size
                           ,show_age_range,show_income_range ,show_gender_percentage ,show_education ,show_occupation ,show_life_stage , bplan_id, segment_id)

        print("DEBUG SQL QUERY:")
        print(sql)   # << print the query
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return


# ==================== B2B CLIENTS CRUD ====================

def add_b2b_client(bplan_id, segment_id, client_name, client_location, client_description=None):
    """Add a new B2B client"""
    conn = None
    client_id = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            INSERT INTO public.buz_b2b_mkt_clients 
            (bplan_id, segment_id, client_name, client_location, client_description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING client_id;
        """
        cur.execute(sql, (bplan_id, segment_id, client_name, client_location, client_description))
        client_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error adding B2B client: {error}")
        return None
    finally:
        if conn is not None:
            conn.close()
    return client_id


def get_b2b_clients(segment_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT client_id, bplan_id, segment_id, client_name, client_location, client_description FROM public.buz_b2b_mkt_clients WHERE segment_id = {};".format(
            segment_id)
        cur.execute(sql)
        rows = cur.fetchall()

        # Convert to list of dictionaries for easier access in template
        clients = []
        for row in rows:
            clients.append({
                'client_id': row[0],
                'bplan_id': row[1],
                'segment_id': row[2],
                'client_name': row[3],
                'client_location': row[4],
                'client_description': row[5]
            })

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error getting B2B clients: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()
    return clients


def delete_b2b_client(client_id):
    """Delete a B2B client"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "DELETE FROM public.buz_b2b_mkt_clients WHERE client_id = %s;"
        cur.execute(sql, (client_id,))

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error deleting B2B client: {error}")
    finally:
        if conn is not None:
            conn.close()


def update_b2b_client(client_id, client_name, client_location, client_description=None):
    """Update a B2B client"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            UPDATE public.buz_b2b_mkt_clients
            SET client_name = %s, client_location = %s, client_description = %s
            WHERE client_id = %s;
        """
        cur.execute(sql, (client_name, client_location, client_description, client_id))

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error updating B2B client: {error}")
    finally:
        if conn is not None:
            conn.close()



# Competitors
def get_buz_competitor(bplan_id):
    conn = None
    try:    
        db_params = config()  
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_competitor where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_competitor ( competitor_name_1st, competitor_name_2nd, competitor_name_3rd, bplan_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_competitor SET competitor_name_1st='{}', competitor_name_2nd='{}', competitor_name_3rd='{}' WHERE bplan_id={} ;".format(competitor_name_1st, competitor_name_2nd, competitor_name_3rd, bplan_id )
        cur.execute(sql)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def update_competitors_preferences ( bplan_id, preference, competitor1_value, competitor2_value, competitor3_value):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        if competitor1_value in ('',None): competitor1_value = 0
        if competitor2_value in ('',None): competitor2_value = 0
        if competitor3_value in ('',None): competitor3_value = 0

        # print(preference, competitor1_value, competitor2_value, competitor3_value)
        sql = "UPDATE public.buz_preferences SET competitor1_value={}, competitor2_value={}, competitor3_value={} WHERE bplan_id={}  and preference='{}' ;".format(competitor1_value, competitor2_value, competitor3_value, bplan_id, preference)
        cur.execute(sql)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

# Operations Plan
def get_buz_operation_plan(bplan_id):
    conn = None
    try:    
        db_params = config()  
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_operation_plan where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_operation_plan ( enhance_production, customer_support, bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_operation_plan SET enhance_production='{}', customer_support='{}' WHERE bplan_id={} ;".format(enhance_production, customer_support, bplan_id )
        print(sql)
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

############################################################################################################################### youssef
def get_buz_supplier(bplan_id):
    """Get suppliers without products"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            SELECT supplier_id, supplier_name, years_of_collaboration, 
                   performance_type, quality, customer_service
            FROM public.buz_suppliers 
            WHERE bplan_id = {}
            ORDER BY supplier_name
        """.format(bplan_id)

        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        cur.close()
        return (results, "")

    except (Exception, psycopg2.DatabaseError) as error:
        return (None, str(error))
    finally:
        if conn is not None:
            conn.close()

def get_products_buz_supplier(supplier_id):
    """Get products for a specific supplier"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            SELECT product_id, supplier_id, bplan_id, product_service, 
                   prices, quantity
            FROM public.buz_suppliers_products_info 
            WHERE supplier_id = {}
        """.format(supplier_id)

        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        cur.close()
        return (results, "")

    except (Exception, psycopg2.DatabaseError) as error:
        return (None, str(error))
    finally:
        if conn is not None:
            conn.close()

def supplier_add(bplan_id, supplier_name, years_of_collaboration, performance_type, quality, customer_service):
    """Add a new supplier (without products)"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Use parameterized query (important for security)
        sql = """
              INSERT INTO public.buz_suppliers
              (bplan_id, supplier_name, years_of_collaboration, performance_type, quality, customer_service)
              VALUES (%s, %s, %s, %s, %s, %s) RETURNING supplier_id \
              """
        cur.execute(sql, (bplan_id, supplier_name, years_of_collaboration,
                          performance_type, quality, customer_service))

        supplier_id = cur.fetchone()[0]
        conn.commit()
        return (supplier_id, "")  # Return new supplier ID
    except (Exception, psycopg2.DatabaseError) as error:
        return (None, str(error))
    finally:
        if conn is not None:
            conn.close()

def supplier_delete(supplier_id):
    """Delete a supplier and all their products (via CASCADE)"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # This will automatically delete products due to ON DELETE CASCADE
        cur.execute("""
                    DELETE
                    FROM public.buz_suppliers
                    WHERE supplier_id = %s
                    """, (supplier_id,))

        conn.commit()
        return (True, "Supplier and all products deleted")
    except (Exception, psycopg2.DatabaseError) as error:
        if conn: conn.rollback()
        return (False, str(error))
    finally:
        if conn is not None:
            conn.close()

def supplier_product_add(supplier_id, bplan_id, product_service, prices, quantity):
    """Add a new product for a supplier"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            INSERT INTO public.buz_suppliers_products_info
            (supplier_id, bplan_id, product_service, prices, quantity)
            VALUES ({}, {}, '{}', '{}', '{}')
            RETURNING product_id
        """.format(supplier_id, bplan_id, product_service, prices, quantity)

        cur.execute(sql)
        product_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        return (product_id, "")

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        return (None, str(error))
    finally:
        if conn is not None:
            conn.close()

def supplier_product_delete(supplier_id, product_id):
    """Delete a specific product from a supplier"""
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # First verify the product exists and belongs to the supplier
        cur.execute("""
                    SELECT 1
                    FROM buz_suppliers_products_info
                    WHERE product_id = %s
                      AND supplier_id = %s
                    """, (product_id, supplier_id))

        if not cur.fetchone():
            return False, "Product not found for this supplier"

        # Then delete the product
        cur.execute("""
                    DELETE
                    FROM buz_suppliers_products_info
                    WHERE product_id = %s
                      AND supplier_id = %s
                    """, (product_id, supplier_id))

        conn.commit()
        return True, "Product deleted successfully"

    except (Exception, psycopg2.DatabaseError) as error:
        if conn: conn.rollback()
        print(f"Error deleting product: {error}")  # Debug logging
        return False, str(error)
    finally:
        if conn is not None:
            conn.close()
###############################################################################################################################
def get_buz_production(bplan_id):
    conn = None
    try:   
        db_params = config()    
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_production where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def production_add (bplan_id, allocated_resources, production_unit, time_frame, current_capacity, max_expected_capacity):
    conn = None
    try:     
        db_params = config()  
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if current_capacity in ('',None): current_capacity = 0
        if max_expected_capacity in ('',None): max_expected_capacity = 0

        sql = "INSERT INTO public.buz_production(bplan_id, allocated_resources, production_unit, time_frame, current_capacity, max_expected_capacity) VALUES ({}, '{}', '{}', '{}', {}, {});".format(bplan_id, allocated_resources, production_unit, time_frame, current_capacity, max_expected_capacity)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def production_delete(production_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_production where production_id = {};".format(production_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_distribution(bplan_id):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_distribution where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def distribution_add (bplan_id, distribution_name, type, collaboration_years):
    conn = None
    try:     
        db_params = config()  
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
         
        if collaboration_years in ('',None): collaboration_years = 0

        sql = "INSERT INTO public.buz_distribution (bplan_id, distribution_name, type, collaboration_years) VALUES ({}, '{}', '{}', {})".format(bplan_id, distribution_name, type, collaboration_years)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def distribution_delete(distribution_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_distribution where distribution_id = {};".format(distribution_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

# Requested Fund
def get_buz_fund_details(bplan_id):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_fund_details where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_fund_details ( project_objectives, project_purposes, fund_type, amount, equity, interest_rate, period, grace_period,  bplan_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_fund_details SET project_objectives='{}', project_purposes='{}', fund_type = '{}', amount = {}, equity = {}, interest_rate = {}, period = {}, grace_period = {}  \
             WHERE bplan_id={} ;".format(project_objectives, project_purposes, fund_type, amount, equity, interest_rate, period, grace_period, bplan_id )
        cur.execute(sql)
        
        cur.close()
        print('we re in the function and type is',fund_type)
        if fund_type == 'loan':
            print('we re in the loan thing')

            # Safely convert inputs to numeric types
            try:
                r = float(interest_rate) / 100
                P = float(amount)
                N = int(period)
                G = int(grace_period)
            except ValueError as e:
                print("Error converting input types:", e)
                return ("*", "Invalid numeric value for loan parameters")

            # Compute yearly value
            if r > 0:
                yearly_payment = P * (r * (1 + r) ** (N - G)) / ((1 + r) ** (N - G) - 1)
            else:
                yearly_payment = P / (N - G)

            yearly_value = (G * (P * r) + (N - G) * yearly_payment) / N

            db_params = config()
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()

            # Check if a record already exists for this loan
            cur.execute("""
                SELECT price FROM public.buz_feasibility_operating_expenses
                WHERE bplan_id = %s AND type = %s
            """, (bplan_id, "Potential Loan Repayment"))
            result = cur.fetchone()
            print(result)

            if result:
                existing_price = result[0]
                if abs(existing_price - yearly_value) < 1e-6:  # small tolerance for float
                    print("Loan entry already exists with same yearly_value — no update needed.")
                else:
                    cur.execute("""
                        UPDATE public.buz_feasibility_operating_expenses
                        SET price = %s
                        WHERE bplan_id = %s AND type = %s
                    """, (yearly_value, bplan_id, "Potential Loan Repayment"))
                    print("Loan entry updated with new yearly_value.")
            else:
                cur.execute("""
                    INSERT INTO public.buz_feasibility_operating_expenses (bplan_id, type, unit_quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (bplan_id, "Potential Loan Repayment", 1, yearly_value))
                print("New loan entry inserted.")

            cur.close()






    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_fund_items(bplan_id, type_id):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_fund_items where bplan_id ={} and type_id = {};".format(bplan_id, type_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        sql = "SELECT sum(total_cost) as total_value FROM public.buz_fund_items WHERE bplan_id ={};".format(bplan_id)
        cur.execute(sql)
        total_result = cur.fetchall()
        if total_result[0][0] == None: total_costs = 0
        else: total_costs = total_result[0][0]

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error, None)
    finally:
        if conn is not None:
            conn.close()
    return (True, results, total_costs)


def buz_item_add(bplan_id, type_id, item, unit, item_quantity, item_cost):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Initialize variables
        total_cost = 0

        # Handle different types
        if type_id == '1':  # Installation
            item = ''
            unit = ''
            item_quantity = 1
            total_cost = int(item_cost)  # Installation is just the cost

        # elif type_id == '4':  # Salaries
        #     item = ''
        #     item_quantity = 1
        #
        #     # Calculate total cost based on time unit
        #     if unit == 'Month':
        #         total_cost = int(item_cost) * 12
        #     elif unit == 'Week':
        #         total_cost = int(item_cost) * 52
        #     elif unit == 'Year':
        #         total_cost = int(item_cost)
        #     elif unit == 'Quarter':
        #         total_cost = int(item_cost) * 4
        #     elif unit == 'Day':
        #         total_cost = int(item_cost) * 365
        #     else:
        #         total_cost = int(item_cost)  # Default case if unit is unexpected

        else:  # Other types (Machinery, Raw Material, etc.)
            if item_quantity in ('', None):
                item_quantity = 0
            if item_cost in ('', None):
                item_cost = 0
            total_cost = int(item_quantity) * int(item_cost)

        sql = """INSERT INTO public.buz_fund_items(bplan_id, type_id, item, unit, quantity, cost, total_cost) \
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        params = (bplan_id, type_id, item, unit, item_quantity, item_cost, total_cost)

        # print(sql, params)
        cur.execute(sql, params)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def buz_item_delete(item_id):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "delete from public.buz_fund_items where item_id = {};".format(item_id)
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

# Feasibility


# Youssef ############################################################################################################

def product_add(bplan_id, product_service_id, unit, price, cost,
                growth_prct_year1, growth_prct_year2, growth_prct_year3,
                growth_prct_year4, growth_prct_year5,
                growth_reason_year1, growth_reason_year2, growth_reason_year3,
                growth_reason_year4, growth_reason_year5):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """UPDATE public.buz_product_services
                 SET unit              = %s, \
                     price             = %s, \
                     cost              = %s,
                     growth_prct_year1 = %s, \
                     growth_prct_year2 = %s,
                     growth_prct_year3 = %s, \
                     growth_prct_year4 = %s,
                     growth_prct_year5 = %s,
                     reason_of_growth_year1 = %s, \
                     reason_of_growth_year2 = %s,
                     reason_of_growth_year3 = %s, \
                     reason_of_growth_year4 = %s,
                     reason_of_growth_year5 = %s
                 WHERE product_service_id = %s \
                   AND bplan_id = %s"""
        cur.execute(sql, (unit, price, cost,
                          growth_prct_year1, growth_prct_year2,
                          growth_prct_year3, growth_prct_year4,
                          growth_prct_year5,
                          growth_reason_year1, growth_reason_year2,
                          growth_reason_year3, growth_reason_year4,
                          growth_reason_year5,
                          product_service_id, bplan_id))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_product(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """SELECT *
                 FROM public.buz_product_services
                 WHERE bplan_id = %s"""
        cur.execute(sql, (bplan_id,))

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append(result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.close()
    return (results, "")


def product_delete(product_service_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql ="""UPDATE public.buz_product_services
                    SET
                        unit = 0,
                        price = 0,
                        cost = 0,
                        growth_prct_year1 = 0,
                        growth_prct_year2 = 0,
                        growth_prct_year3 = 0,
                        growth_prct_year4 = 0,
                        growth_prct_year5 = 0,
                        reason_of_growth_year1 = 'None',
                        reason_of_growth_year2 = 'None',
                        reason_of_growth_year3 = 'None',
                        reason_of_growth_year4 = 'None',
                        reason_of_growth_year5 = 'None'
                    WHERE product_service_id = %s"""
        cur.execute(sql, (product_service_id,))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return


############################################################################################################


def get_buz_feasibility(bplan_id):
    conn = None
    try:   
        db_params = config()    
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_feasibility where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_feasibility ( first_year, second_year, third_year, fourth_year, fifth_year, annual_growth, depreciation, bplan_id ):
    conn = None
    try:   
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_feasibility SET first_year={}, second_year={}, third_year={}, fourth_year={}, fifth_year={}, annual_growth={}, depreciation={} WHERE bplan_id={} ;".format( first_year, second_year, third_year, fourth_year, fifth_year, annual_growth, inflation_rate, depreciation, bplan_id )
        cur.execute(sql)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return


def expense_add(bplan_id, expense_type, unit_quantity, price):
    print('we re in the funcc')
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """INSERT INTO public.buz_feasibility_operating_expenses 
                 (bplan_id, type, unit_quantity, price)
                 VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, (bplan_id, expense_type, unit_quantity, price))
        print(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def get_buz_expenses(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """SELECT id, bplan_id, type, unit_quantity, price
                 FROM public.buz_feasibility_operating_expenses
                 WHERE bplan_id = %s
                 ORDER BY id"""
        cur.execute(sql, (bplan_id,))

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append(result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def feasibilty_expense_delete(expense_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # 1) Fetch expense type
        cur.execute(
            "SELECT type FROM public.buz_feasibility_operating_expenses WHERE id = %s",
            (expense_id,)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return ("not_found", "Expense not found")

        expense_type = (row[0] or "").strip()

        # 2) Block deletion for Potential Loan Repayment (case-insensitive)
        if expense_type.lower() == 'potential loan repayment':
            cur.close()
            return ("blocked", {
                "en": "You cannot delete this expense. You can go back to Requested Fund to delete or edit it.",
                "ar": "لا يمكنك حذف هذا المصروف. يمكنك الرجوع إلى طلب التمويل لحذفه أو تعديله."
            })

        # 3) Proceed with delete
        cur.execute(
            "DELETE FROM public.buz_feasibility_operating_expenses WHERE id = %s",
            (expense_id,)
        )

        cur.close()

        # mark success so we know to commit
        deleted = True

    except (Exception, psycopg2.DatabaseError) as error:
        # keep your existing error pattern
        return ("*", error)
    finally:
        if conn is not None:
            # commit only when a deletion occurred; otherwise rollback
            if 'deleted' in locals() and deleted:
                conn.commit()
            else:
                try:
                    conn.rollback()
                except Exception:
                    pass
            conn.close()

    return ("ok",)


def get_buz_inflation_rate(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select inflation_rate from public.buz_feasibility where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def update_buz_inflation_rate(inflation_rate, bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_feasibility SET inflation_rate = %s WHERE bplan_id = %s;"
        cur.execute(sql, (inflation_rate, bplan_id))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return

def calculate_projections(products, expenses, inflation_rate):
    projections = []
    inflation_factor = 1 + (inflation_rate / 100)

    # Initialize grand totals structure
    total_projections = {
        'years': [{
            'grand_total_revenue': 0,
            'grand_total_cost': 0,
            'total_operating_expenses': 0,
            'profit': 0,
            'margin': 0
        } for _ in range(6)],
        'inflation_rate': inflation_rate
    }

    # --- PRODUCTS CALCULATION ---
    if not products:
        projections.append(create_empty_product_projection())
    else:
        for product in products:
            projection = calculate_product_projection(product, inflation_factor)
            projections.append(projection)

            # Update grand totals
            for year in range(6):
                total_projections['years'][year]['grand_total_revenue'] += projection['totals']['revenue'][year]
                total_projections['years'][year]['grand_total_cost'] += projection['totals']['cost'][year]

    # --- OPERATING EXPENSES CALCULATION ---
    if not expenses:
        projections.append(create_empty_expense_projection())
        projections.append(create_empty_total_expense_projection())
    else:
        # Calculate individual expenses and track yearly totals
        yearly_expense_totals = [0] * 6

        for expense in expenses:
            expense_proj = calculate_expense_projection(expense, inflation_factor)
            projections.append(expense_proj)

            # Update yearly expense totals
            for year in range(6):
                yearly_expense_totals[year] += expense_proj['years'][year]['amount']
                total_projections['years'][year]['total_operating_expenses'] += expense_proj['years'][year]['amount']

        # Add total operating expenses row
        total_expense_proj = create_total_expense_projection(expenses, yearly_expense_totals)
        projections.append(total_expense_proj)

    # --- FINAL TOTALS CALCULATION ---
    calculate_final_totals(total_projections)

    return projections, total_projections

# Helper functions
def create_empty_product_projection():
    return {
        'name': 'No Products Added',
        'type': 'product',
        'years': [{
            'quantity': 0,
            'revenue': 0,
            'cost': 0,
            'price_per_unit': 0,
            'cost_per_unit': 0
        } for _ in range(6)],
        'base_price': 0,
        'base_cost': 0,
        'totals': {
            'revenue': [0] * 6,
            'cost': [0] * 6
        }
    }
def calculate_product_projection(product, inflation_factor):
    projection = {
        'name': product['product_service_name'],
        'type': 'product',
        'years': [],
        'base_price': float(product['price']),
        'base_cost': float(product['cost']),
        'totals': {
            'revenue': [0] * 6,
            'cost': [0] * 6
        }
    }

    current_qty = float(product['unit'])

    for year in range(6):
        # Apply growth rate (except year 0)
        if year > 0:
            growth_rate = float(product.get(f'growth_prct_year{year}', 0)) / 100 + 1
            current_qty *= growth_rate

        # Apply inflation
        year_inflation = inflation_factor ** year
        current_price = projection['base_price'] * year_inflation
        current_cost = projection['base_cost'] * year_inflation
        revenue = current_qty * current_price
        cost = current_qty * current_cost

        projection['years'].append({
            'quantity': current_qty,
            'revenue': revenue,
            'cost': cost,
            'price_per_unit': current_price,
            'cost_per_unit': current_cost
        })

        # Store per-product totals
        projection['totals']['revenue'][year] = revenue
        projection['totals']['cost'][year] = cost

    return projection
def create_empty_expense_projection():
    return {
        'name': 'No Expenses Added',
        'type': 'expense',
        'years': [{
            'amount': 0,
            'base_amount': 0
        } for _ in range(6)],
        'base_amount': 0
    }
def create_empty_total_expense_projection():
    return {
        'name': 'Total Operating Expenses',
        'type': 'expense_total',
        'years': [{
            'amount': 0,
            'base_amount': 0
        } for _ in range(6)],
        'base_amount': 0
    }
def calculate_expense_projection(expense, inflation_factor):
    quantity = float(expense.get('unit_quantity', 1))
    base_price = float(expense['price'])

    expense_proj = {
        'name': expense['type'],
        'type': 'expense',
        'years': [],
        'base_amount': base_price
    }

    for year in range(6):
        inflated_price = base_price * (inflation_factor ** year)
        total_amount = inflated_price * quantity

        expense_proj['years'].append({
            'amount': total_amount,
            'base_amount': base_price
        })

    return expense_proj
def create_total_expense_projection(expenses, yearly_totals):
    return {
        'name': 'Total Operating Expenses',
        'type': 'expense_total',
        'years': [{
            'amount': yearly_totals[year],
            'base_amount': sum(float(e['price']) * float(e.get('unit_quantity', 1)) for e in expenses)
        } for year in range(6)],
        'base_amount': sum(float(e['price']) * float(e.get('unit_quantity', 1)) for e in expenses)
    }
def calculate_final_totals(total_projections):
    for year in range(6):
        year_data = total_projections['years'][year]

        # Profit = Revenue - (Cost + Expenses)
        year_data['profit'] = year_data['grand_total_revenue'] - (
                year_data['grand_total_cost'] + year_data['total_operating_expenses']
        )

        # Margin calculation
        year_data['margin'] = (
            (year_data['profit'] / year_data['grand_total_revenue']) * 100
            if year_data['grand_total_revenue'] > 0
            else 0
        )

        # Rounding
        for key in year_data:
            if isinstance(year_data[key], (int, float)):
                year_data[key] = round(year_data[key], 2) if key != 'margin' else round(year_data[key], 1)

################################################################################################################################################################
# export plan


def update_buz_export_plan_checkboxes(complete_client_profile,complete_business_profile,complete_business_premises,complete_market_analysis,complete_competitors,complete_operations_plan,complete_requested_fund,complete_feasibility,bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            UPDATE public.buz_export_plan
            SET
                complete_client_profile = %s,
                complete_business_profile = %s,
                complete_business_premises = %s,
                complete_market_analysis = %s,
                complete_competitors = %s,
                complete_operations_plan = %s,
                complete_requested_fund = %s,
                complete_feasibility = %s
            WHERE bplan_id = %s;
        """
        cur.execute(sql, (
            complete_client_profile,
            complete_business_profile,
            complete_business_premises,
            complete_market_analysis,
            complete_competitors,
            complete_operations_plan,
            complete_requested_fund,
            complete_feasibility,
            bplan_id
        ))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("❌ Error updating buz_export_plan:", error)
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

    return


def get_buz_export_plan_checkboxes(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            SELECT 
                complete_client_profile,
                complete_business_profile,
                complete_business_premises,
                complete_market_analysis,
                complete_competitors,
                complete_operations_plan,
                complete_requested_fund,
                complete_feasibility
            FROM public.buz_export_plan
            WHERE bplan_id = %s;
        """

        cur.execute(sql, (bplan_id,))
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("❌ Error fetching buz_export_plan checkboxes:", error)
        return ("*", error)
    finally:
        if conn is not None:
            conn.close()

    return (result, "")

def get_export_plan(bplan_id):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_export_plan where bplan_id ={};".format(bplan_id)
        cur.execute(sql)

        columns = [column[0] for column in cur.description]
        results = []

        for row in cur.fetchall():
            result = dict(zip(columns, row))
            results.append (result)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return ("*", error )
    finally:
        if conn is not None:
            conn.close()
    return (results, "")

def get_api_content_client_info(client, query_model, bplan_id, lang='en'):
    print(f"DEBUG: get_api_content_client_info started for bplan_id={bplan_id}")
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "UPDATE public.buz_export_plan SET client_avatar=(SELECT client_avatar FROM public.client_info WHERE bplan_id = {}), \
            full_name =(SELECT full_name FROM public.client_info WHERE bplan_id = {}) WHERE bplan_id = {};".format(bplan_id, bplan_id, bplan_id)
        cur.execute(sql)

        sql = "SELECT 'The name is ' || full_name || '.  gender is ' || gender || '. marital status is ' || marital_status || CASE WHEN number_of_children = 0  THEN '' ELSE ' with number of children equals to ' ||  number_of_children END || '. nationality is ' || nationality || '. date of birth ' || TO_CHAR(dob, 'DD/MM/YYYY') || '. the education level is ' || education_level || '.  years of experience equals to ' || years_of_experience || '.  the education major is ' || education_major || ' profession in ' || specialty || '. the education institution is ' || education_institution as api_content FROM public.client_info WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_client_profile = ''
        else:
            results = cur.fetchall()

            user_prompt ="write a professional user profile business plan that is almost two paragraphs and approcimately 150 words. using third person pronoun. include the following information: (You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content.)"
            # 👇 Add this conditional part for Arabic
            if lang == "ar":
                user_prompt += " Do it in Arabic."
                print('we re in the arrr')

            query_messages = [
                            {"role": "user", "content": user_prompt },
                            {"role": "user", "content": results[0][0] }
                            ]
            print(user_prompt)
            try:
                result_client_profile = client.chat.completions.create(model=query_model, messages=query_messages)
                chatgpt_client_profile = result_client_profile.choices[0].message.content.replace("'", "''")
                print(f"DEBUG: OpenAI generated content (first 100 chars): {chatgpt_client_profile[:100]}")
            except Exception as e:
                print(f"ERROR: OpenAI call failed: {e}")

        sql = "UPDATE public.buz_export_plan SET client_profile = '{}' WHERE bplan_id = {};".format(chatgpt_client_profile, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_client_experience(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT ' experience of ' || years_of_experience || ' years as ' || field as api_content FROM public.experiences WHERE bplan_id = {} \
            UNION SELECT 'gender is ' || gender || ' but do not mention it.' FROM public.client_info as api_content WHERE bplan_id = {}; ".format(bplan_id, bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_client_experience = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)

            base_prompt = """You are a professional business writer. Create a concise professional background paragraph (approximately 80-120 words) that:

            1. Highlights the individual's professional experience and expertise
            2. Uses formal third-person business language
            3. Emphasizes relevant skills and industry knowledge
            4. Avoids list-like structures and repetition
            5. Presents a cohesive narrative of professional development
            6. Output a single, continuous paragraph only.
            
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            
            query_messages = [
                    {"role": "user", "content":base_prompt},
                    {"role": "user", "content": results}
                    ]
            result_client_experience = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_client_experience = result_client_experience.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET client_experiences = '{}' WHERE bplan_id = {};".format(chatgpt_client_experience, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_client_partners(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = " SELECT ' partner name ' || partner_name || ', the partner relation is ' || partner_relation || ', the partner years of experience is ' || partner_years_of_experience || ' as ' || partner_experience || '.' as api_content FROM public.partners WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_client_partners = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create a strategic partnership overview paragraph (approximately 80-120 words) that:

            1. Describes key business partners and their contributions
            2. Highlights collaborative strengths and shared expertise
            3. Uses formal third-person business language
            4. Avoids bullet points and repetitive phrasing
            5. Emphasizes the strategic value of these partnerships
            6. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
                
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results }
                    ]
            result_client_partners = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_client_partners = result_client_partners.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET client_partners = '{}' WHERE bplan_id = {};".format(chatgpt_client_partners, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_client_expenses(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = " SELECT ' the living expenses for ' || living_expenses || ' is equal to ' || value || ' USD per ' || case when unit = 1 then 'year.' when unit = 2 then 'month.' end as api_content FROM public.expenses WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_client_expenses = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create a concise living expenses context paragraph (approximately 80-100 words) that:

            1. Provides appropriate context about living expenses
            2. Uses formal third-person business language
            3. Maintains professional tone without excessive detail
            4. Avoids list-like structures and repetition
            5. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results}
                    ]
            result_client_expenses = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_client_expenses = result_client_expenses.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET client_expenses = '{}' WHERE bplan_id = {};".format(chatgpt_client_expenses, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_client_employed(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT ' working for ' || emp_where || ' as ' || emp_job_hold || ' working location ' || emp_location || ' for the perior of ' || emp_duration || ' years with monthly income of ' || emp_monthly_income as api_content FROM public.employed WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_client_employed = ''
        else:
            results = cur.fetchall()
            base_prompt = """You are a professional business writer. Create a professional employment background paragraph (approximately 80-100 words) that:

            1. Describes current employment situation and relevant experience
            2. Uses formal third-person business language
            3. Highlights relevant professional context
            4. Avoids list-like structures and repetition
            5. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results[0][0] }
                    ]
            result_client_employed = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_client_employed = result_client_employed.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET client_employed = '{}' WHERE bplan_id = {};".format(chatgpt_client_employed, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_client_side_business(client, query_model, bplan_id, lang='en'):
    print('we re in get_api_content_client_side_business')
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = f"""
            SELECT 
                'the side business name is ' || t1.buz_name ||
                ' industry ' || t2.industry ||
                ' location ' || t1.buz_location ||
                ' since ' || t1.buz_duration || ' years with monthly income of ' ||
                t1.buz_monthly_income || ' USD' AS api_content
            FROM public.side_business t1
            LEFT JOIN lst_industries t2 
                ON t1.buz_industry = t2.industry_id::text
            WHERE t1.bplan_id = {bplan_id};
        """
        cur.execute(sql)
        result = cur.fetchone()  # ✅ fetch only one row since you only use results[0][0]

        if not result or not result[0]:
            chatgpt_client_side_business = ''
        else:
            api_content = result[0]
            base_prompt="""You are a professional business writer. 
                        Rewrite the following information into a polished and concise paragraph suitable for inclusion in a business report. 
                        Use a formal, third-person tone and avoid repeating words or using list-like phrasing. 
                        The paragraph should flow naturally, be about 80–100 words, 
                        and clearly highlight the business name, industry, location, years of operation, and monthly income. 
                        You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content.
                        Information to transform:"""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                { "role": "user","content": base_prompt},
                {"role": "user", "content": api_content},
            ]

            response = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_client_side_business = response.choices[0].message.content.replace("'", "''")

        update_sql = f"""
            UPDATE public.buz_export_plan 
            SET side_business = '{chatgpt_client_side_business}' 
            WHERE bplan_id = {bplan_id};
        """
        cur.execute(update_sql)
        print(chatgpt_client_side_business)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("❌ Error:", error)
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_business_profile(client, query_model, bplan_id, lang='en'):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT ' brand name is ' || buz_name || ' established since ' || TO_CHAR(buz_est_date, 'DD/MM/YYYY')  || '. Located in ' || buz_address || '. business model ' ||  buz_model as api_content FROM public.buz_info WHERE bplan_id = {};".format(
            bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_business_profile = ''
        else:
            results = cur.fetchall()

            base_prompt = """You are a professional business writer. Create a compelling company overview paragraph (approximately 120-180 words) that:

            1. Presents the company's brand, establishment, and business model
            2. Uses formal third-person business language
            3. Highlights unique value proposition and market positioning
            4. Avoids list-like structures and repetition
            5. Creates a cohesive narrative about the business
            6. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."

            query_messages = [
                {"role": "user", "content": base_prompt},
                {"role": "user", "content": results[0][0]}
            ]

            # API call with error handling
            try:
                result_business_profile = client.chat.completions.create(model=query_model, messages=query_messages)
                chatgpt_business_profile = result_business_profile.choices[0].message.content.replace("'", "''")
            except Exception as api_error:
                print(f"ERROR: API call failed: {api_error}")
                return (False, f"API call failed: {str(api_error)}")

        # Use parameterized query for UPDATE
        update_sql = "UPDATE public.buz_export_plan SET business_profile = %s WHERE bplan_id = %s;"
        cur.execute(update_sql, (chatgpt_business_profile, bplan_id))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: Database operation failed: {error}")
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_buz_product_services(client, query_model, bplan_id, lang='en'):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Step 1: Fetch product/services info
        sql = """
        SELECT 
            'Product/Service name: ' || product_service_name ||
            ', Description: ' || COALESCE(product_service_description, 'No description') 
        AS api_content
        FROM public.buz_product_services 
        WHERE bplan_id = %s;
        """
        cur.execute(sql, (bplan_id,))
        rows = cur.fetchall()

        if not rows:
            chatgpt_product_services = ''
        else:
            # Prepare concatenated content
            results = [row[0] for row in rows]
            content_input = " and ".join(results)

            # --- Build multilingual prompt
            base_prompt = """Write a professional description of the products and services offered by 
                    this business in about 100 words using a third-person perspective. 
                    Combine and rewrite the information below into a coherent, polished paragraph.
                    You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."


            query_messages = [
                {"role": "user", "content": base_prompt},
                {"role": "user", "content": content_input}
            ]

            # Step 2: Generate description with GPT
            result = client.chat.completions.create(
                model=query_model,
                messages=query_messages
            )

            chatgpt_product_services = result.choices[0].message.content.replace("'", "''")

        # Step 3: Update export plan
        sql_update = """
        UPDATE public.buz_export_plan 
        SET buz_product_services = %s 
        WHERE bplan_id = %s;
        """
        cur.execute(sql_update, (chatgpt_product_services, bplan_id))

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"API PRODUCT/SERVICES ERROR: {error}")
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

    return (True, "")

def get_api_content_buz_staff(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT ' Total Salary ' || sum(total_salary) || ' USD.' as api_content FROM public.buz_staff WHERE bplan_id ={} \
            UNION SELECT ' the staff position is ' || staff_position || ' working as ' || work_time || ' with monthly salary of ' || staff_salary || ' USD.' as api_content FROM public.buz_staff WHERE bplan_id ={} ORDER by 1;".format(bplan_id, bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_buz_staff = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create a professional team structure overview paragraph (approximately 80-120 words) that:

            1. Describes the organizational structure and key positions
            2. Uses formal third-person business language
            3. Highlights team composition and resource allocation
            4. Avoids listing individual salaries or repetitive details
            5. Emphasizes the strength of the human resources
            6. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results }
                    ]
            result_buz_staff = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_buz_staff = result_buz_staff.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET buz_staff = '{}' WHERE bplan_id = {};".format(chatgpt_buz_staff, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_buz_resources(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT ' Total resource equals to ' || sum(resource_value) || ' USD ' as api_content FROM public.buz_resource WHERE bplan_id = {} \
                UNION SELECT ' There are ' || resource_subtype || ' with value equals to ' || resource_value || ' USD ' as api_content FROM public.buz_resource WHERE bplan_id = {};" .format(bplan_id, bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_buz_resource = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create an asset and resource overview paragraph (approximately 80-120 words) that:

            1. Describes the company's existing resources and assets
            2. Uses formal third-person business language
            3. Highlights the value and strategic importance of resources
            4. Avoids list-like structures and direct enumeration
            5. Emphasizes operational capacity and resource strength
            6. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results }
                    ]
            result_buz_resource = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_buz_resource = result_buz_resource.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET buz_resource = '{}' WHERE bplan_id = {};".format(chatgpt_buz_resource, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_source_funding(client, query_model, bplan_id, lang='en'):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # FIX 1: Use parameterized queries for security
        sql = """
        SELECT 'We have ' || funds || ' funding source contributing ' || contribution || '% to the business' 
        FROM buz_other_resource 
        WHERE bplan_id = {};
        """.format(bplan_id )
        cur.execute(sql)  # Pass parameters as tuple
        if cur.rowcount == 0:
            chatgpt_source_funding = ''
        else:
            results = []
            for row in cur.fetchall():
                results.append(row[0])

            results = ' and '.join(results)

            base_prompt = """You are a professional business writer. Create a concise funding sources paragraph (approximately 100-150 words) that:
                            
                            1. Describes current funding sources and their contributions
                            2. Uses formal third-person business language
                            3. Highlights financial backing and investor confidence
                            4. Avoids list-like structures and repetition
                            5. Emphasizes financial stability and support
                            6. Output a single, continuous paragraph only
                            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""

            # FIX 2: More explicit language instruction
            if lang == "ar":
                base_prompt += "\n\nWrite the entire response in Arabic language."
            else:
                base_prompt += "\n\nWrite the entire response in English language."

            query_messages = [
                {"role": "user", "content": base_prompt},
                {"role": "user", "content": results}
            ]

            # FIX 3: Add API error handling
            try:
                result_source_funding = client.chat.completions.create(
                    model=query_model,
                    messages=query_messages
                )
                if result_source_funding.choices and len(result_source_funding.choices) > 0:
                    chatgpt_source_funding = result_source_funding.choices[0].message.content.replace("'", "''")
                else:
                    chatgpt_source_funding = "Error: No response from AI API"
            except Exception as api_error:
                print(api_error)
                return (False, f"API call failed: {str(api_error)}")

        # FIX 4: Use parameterized query for UPDATE as well
        update_sql = "UPDATE public.buz_export_plan SET source_of_funding = %s WHERE bplan_id = %s;"
        cur.execute(update_sql, (chatgpt_source_funding, bplan_id))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_financial_history(client, query_model, bplan_id, lang='en'):
    print(0)
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Remove %s and use .format() directly
        sql = """
        select 'for the year '||t1.financial_year||' the sales reached '||t1.financial_sales||' '||t2.buz_currency||' and the net profit was ' ||t1.financial_profit||' '||t2.buz_currency from buz_financial_history t1 
		left join public.bplan t2 on t1.bplan_id=t2.bplan_id
		where t1.bplan_id= {} order by t1.financial_year asc;
        """.format(bplan_id)

        cur.execute(sql)
        print(sql)

        if cur.rowcount == 0:
            chatgpt_financial_history = ''  # Fixed variable name
        else:
            results = []
            for row in cur.fetchall():
                results.append(row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create a financial performance overview paragraph (approximately 100-150 words) that:

            1. Summarizes historical financial performance and trends
            2. Uses formal third-person business language
            3. Highlights growth patterns and financial stability
            4. Avoids year-by-year listing and repetitive phrasing
            5. Emphasizes consistent performance and growth trajectory
            6. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."

            query_messages = [
                {"role": "user",
                 "content": base_prompt},
                {"role": "user", "content": results}
            ]
            result_financial_history = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_financial_history = result_financial_history.choices[0].message.content.replace("'", "''")

        # Also fixed variable name here
        sql = "UPDATE public.buz_export_plan SET financial_history = '{}' WHERE bplan_id = {};".format(
            chatgpt_financial_history, bplan_id)
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_business_premises(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT ' the premise is located in ' || premise_address || ' with an area of ' || plot_area || ' square meters. ' || 'the premise is a ' || premise_nature || ' \
                surrounded by ' || premise_surrounding || ' and the premise is ' || premise_ownership || \
                CASE WHEN premise_ownership = 'Partially Owned' THEN '. the partner name is ' || partner_name || ' with percentage of ownership equals to ' || percentage_of_ownership \
                WHEN premise_ownership = 'Rented' THEN '. the rent is ' || rent_fees || ' USD every ' || rent_period || ' ' || rent_unit ELSE ''  END FROM public.buz_premise WHERE bplan_id = {} ;".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_business_premises = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create a facility and location overview paragraph (approximately 120-180 words) that:

            1. Describes the business premises, location, and facilities
            2. Uses formal third-person business language
            3. Highlights strategic advantages of the location
            4. Avoids list-like structures and repetition
            5. Emphasizes operational suitability and infrastructure
            6. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results }
                    ]
            result_business_premises = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_business_premises = result_business_premises.choices[0].message.content.replace("'", "''")
        
        sql = "UPDATE public.buz_export_plan SET business_premises = '{}' WHERE bplan_id = {};".format(chatgpt_business_premises, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_market_analysis(client, query_model, bplan_id, lang='en'):
    # print("I'm In get_api_content_market_analysis")
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Build the detailed description for each segment
        sql = f"""
        SELECT 
            'Segment "' || b.segment_name || '" represents ' || b.segment_percentage || 
            '% of the total business. The business model is ' ||
            CASE 
                WHEN b.business_model = 'B2B' THEN 'Business to Business (B2B).'
                WHEN b.business_model = 'B2C' THEN 'Business to Consumer (B2C).'
                ELSE ''
            END ||

            /* ---------------- B2B SECTION ---------------- */
            CASE 
                WHEN b.business_model = 'B2B' THEN
                    COALESCE(
                        (
                            SELECT ' Their top B2B clients include: ' || 
                                STRING_AGG(
                                    c.client_name || ' located in ' || c.client_location ||
                                    CASE 
                                        WHEN c.client_description IS NOT NULL AND c.client_description != '' 
                                        THEN ' (' || c.client_description || ')'
                                        ELSE ''
                                    END,
                                    ', '
                                ) || '.'
                            FROM buz_b2b_mkt_clients c
                            WHERE c.segment_id = b.segment_id
                        ),
                        ' This B2B segment has not yet identified specific key clients.'
                    )
                ELSE ''
            END ||
            CASE 
                WHEN b.business_model = 'B2B' AND b.preferences IS NOT NULL AND b.preferences != '' THEN
                    ' Their clients enjoy ' || b.preferences || '.'
                ELSE ''
            END ||

            /* ---------------- B2C SECTION ---------------- */
            CASE 
                WHEN b.business_model = 'B2C' AND b.show_age_range = 'on' THEN
                    ' The segment age range is between ' || b.age_min || ' and ' || b.age_max || ' years.'
                ELSE ''
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.show_income_range = 'on' THEN
                    ' The segment income range is between ' || b.income_min || ' and ' || b.income_max || ' USD.'
                ELSE ''
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.show_gender_percentage = 'on' THEN
                    ' Gender distribution is ' || b.male_rate || '% male and ' || b.female_rate || '% female.'
                ELSE ''
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.show_occupation = 'on' THEN
                    ' The segment occupations include ' ||
                    TRIM(BOTH ',' FROM (
                        CASE WHEN position('1' in b.occupation)>0 THEN ', Students' ELSE '' END ||
                        CASE WHEN position('2' in b.occupation)>0 THEN ', Employees' ELSE '' END ||
                        CASE WHEN position('3' in b.occupation)>0 THEN ', Business Owners' ELSE '' END ||
                        CASE WHEN position('4' in b.occupation)>0 THEN ', Unemployed' ELSE '' END ||
                        CASE WHEN position('5' in b.occupation)>0 THEN ', Retired' ELSE '' END
                    )) || '.'
                ELSE '' 
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.show_education = 'on' THEN
                    ' The education levels are ' ||
                    TRIM(BOTH ',' FROM (
                        CASE WHEN position('1' in b.education)>0 THEN ', University level' ELSE '' END ||
                        CASE WHEN position('2' in b.education)>0 THEN ', Secondary level' ELSE '' END ||
                        CASE WHEN position('3' in b.education)>0 THEN ', Technical institute' ELSE '' END ||
                        CASE WHEN position('4' in b.education)>0 THEN ', Elementary level' ELSE '' END ||
                        CASE WHEN position('5' in b.education)>0 THEN ', Illiterate' ELSE '' END
                    )) || '.'
                ELSE '' 
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.show_life_stage = 'on' THEN
                    ' The life stages include ' ||
                    TRIM(BOTH ',' FROM (
                        CASE WHEN position('1' in b.life_stage)>0 THEN ', Young single' ELSE '' END ||
                        CASE WHEN position('2' in b.life_stage)>0 THEN ', Newly married no children' ELSE '' END ||
                        CASE WHEN position('3' in b.life_stage)>0 THEN ', 1 to 2 children' ELSE '' END ||
                        CASE WHEN position('4' in b.life_stage)>0 THEN ', 3 to 4 children' ELSE '' END ||
                        CASE WHEN position('5' in b.life_stage)>0 THEN ', More than 5 children' ELSE '' END
                    )) || '.'
                ELSE '' 
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.location IS NOT NULL AND b.location != '' THEN
                    ' They are located in ' || b.location || '.'
                ELSE ''
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.preferences IS NOT NULL AND b.preferences != '' THEN
                    ' Their clients enjoy ' || b.preferences || '.'
                ELSE ''
            END ||
            CASE 
                WHEN b.business_model = 'B2C' AND b.market_channel IS NOT NULL AND b.market_channel != '' THEN
                    ' Their marketing strategy focuses on ' || 
                    COALESCE((
                        SELECT STRING_AGG(l.channel, ', ')
                        FROM lst_mkt_channels l,
                             unnest(
                                 string_to_array(
                                     translate(b.market_channel, '[] ', ''),
                                     ','
                                 )::int[]
                             ) AS mc(id)
                        WHERE l.channel_id = mc.id
                    ), 'various channels') || '.'
                ELSE ''
            END
        AS api_content
        FROM public.buz_mkt_analysis b
        WHERE b.bplan_id = {bplan_id};
        """

        cur.execute(sql)
        rows = cur.fetchall()

        if not rows:
            chatgpt_market_analysis = ''
        else:
            # Combine all segment texts into one narrative
            segment_count = len(rows)
            combined_text = f"The business plan includes {segment_count} market segment{'s' if segment_count > 1 else ''}. "
            for idx, row in enumerate(rows, start=1):
                combined_text += f"Segment {idx}: {row[0]} "

            base_prompt = """You are writing a professional market analysis section for an executive business plan. 

Your task:
1. Write a cohesive, executive-style market analysis (150-200 words)
2. Begin by stating the total number of market segments
3. For each segment, clearly describe:
   - The segment name and its percentage of the total business
   - The business model (B2B or B2C)
   - For B2B segments: List the key clients by name and location if provided, along with any relevant descriptions
   - For B2C segments: Describe the target demographics, behaviors, and marketing channels
   - Any customer preferences or behaviors mentioned

Guidelines:
- Use third-person, professional business language
- Create smooth transitions between segments
- Maintain a formal, analytical tone
- Do NOT invent, assume, or add any information not explicitly provided
- If B2B clients are listed, mention them by name and location
- Present the information in a logical, flowing narrative rather than bullet points
- Focus on painting a clear picture of the market landscape

CRITICAL: Use ONLY the information provided below. Do not make up statistics, client names, locations, or any other details."""

            if lang == "ar":
                base_prompt += "\n\nIMPORTANT: Write the entire analysis in Arabic, maintaining the same professional business tone."

            # Create prompt for ChatGPT
            query_messages = [
                {"role": "system", "content": "You are an expert business analyst writing professional market analysis sections for business plans."},
                {"role": "user", "content": base_prompt},
                {"role": "user", "content": f"Market segment information:\n\n{combined_text}"}
            ]

            result_market_analysis = client.chat.completions.create(
                model=query_model,
                messages=query_messages,
                temperature=0.7,
                max_tokens=500
            )

            chatgpt_market_analysis = result_market_analysis.choices[0].message.content.replace("'", "''")

        # Update final text into database
        sql_update = f"""
        UPDATE public.buz_export_plan 
        SET market_analysis = '{chatgpt_market_analysis}' 
        WHERE bplan_id = {bplan_id};
        """
        cur.execute(sql_update)
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error in get_api_content_market_analysis: {error}")
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

    return (True, "")

def get_api_content_buz_suppliers(client, query_model, bplan_id, lang='en'):
    conn = None
    try:
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            SELECT 
                'The supplier name is ' || s.supplier_name || 
                ' for the business with ' || s.years_of_collaboration || 
                ' collaboration years. Their quality performance is ' || s.quality || 
                ', their customer service performance is ' || s.customer_service || 
                '. They offer the following products: ' ||
                STRING_AGG(
                    p.product_service || ' at price ' || p.prices || ' with quantity ' || p.quantity, 
                    ', '
                ) || '.' as api_content 
            FROM public.buz_suppliers s
            JOIN public.buz_suppliers_products_info p ON s.supplier_id = p.supplier_id
            WHERE s.bplan_id = {}
            GROUP BY s.supplier_id, s.supplier_name, s.years_of_collaboration, s.quality, s.customer_service;
        """.format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_buz_suppliers = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)
            base_prompt = """You are a professional business writer. Create a concise supplier overview paragraph (approximately 100 words) for a business plan that:

            1. Lists all supplier names in a flowing narrative
            2. Highlights their collective strengths and collaboration tenure  
            3. Mentions their key product/service offerings
            4. Uses formal third-person business language
            5. Avoids bullet points and repetitive phrasing
            6. Emphasizes strategic partnership value

            Structure the response as a single, cohesive paragraph suitable for the "Supplier Relationships" section.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."

            query_messages = [
                {
                    "role": "user",
                    "content": base_prompt
                },
                {
                    "role": "user",
                    "content": results
                }
            ]
            result_buz_suppliers = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_buz_suppliers = result_buz_suppliers.choices[0].message.content.replace("'", "''")

        
        sql = "UPDATE public.buz_export_plan SET buz_suppliers = '{}' WHERE bplan_id = {};".format(chatgpt_buz_suppliers, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_buz_production(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT 'The allocated resource ' || allocated_resources || ' with production capacity for ' || production_unit || ' per ' || time_frame || ' has current capacity equals to ' || current_capacity || ' and maximum expected capacity equals to ' || max_expected_capacity || '.' as api_content FROM public.buz_production WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_buz_production = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)

            base_prompt1 = """  "write a professional operation plan that is almost one paragraphs and approcimately 100 words. use third thing pronoun. include the following information:"""
            if lang == "ar":
                base_prompt1 += "(Do it in Arabic.)"

            query_messages = [
                    {"role": "user", "content": base_prompt1},
                    {"role": "user", "content": results }
                    ]

            result_buz_production = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_buz_production = result_buz_production.choices[0].message.content.replace("'", "''")
            
        sql = """
        SELECT 
            'The approaches used here to enhance production includes : ' || 
            CASE WHEN position('1' in enhance_production)>0 THEN 'Recruiting, ' ELSE '' END || 
            CASE WHEN position('2' in enhance_production)>0 THEN 'Staff Training, ' ELSE '' END || 
            CASE WHEN position('3' in enhance_production)>0 THEN 'Improved Equipment, ' ELSE '' END || 
            CASE WHEN position('4' in enhance_production)>0 THEN 'Inventory Management, ' ELSE '' END || 
            CASE WHEN position('5' in enhance_production)>0 THEN 'Quality Control, ' ELSE '' END || 
            CASE WHEN position('6' in enhance_production)>0 THEN 'Regular Maintenance, ' ELSE '' END || 
            CASE WHEN position('7' in enhance_production)>0 THEN 'Advanced Tools & Technology, ' ELSE '' END || 
            '. Customer support services include: ' ||
            CASE WHEN position('1' in customer_support)>0 THEN 'Return Policy, ' ELSE '' END || 
            CASE WHEN position('2' in customer_support)>0 THEN 'Maintenance, ' ELSE '' END || 
            CASE WHEN position('3' in customer_support)>0 THEN 'Warranty, ' ELSE '' END || 
            CASE WHEN position('4' in customer_support)>0 THEN 'Customer Feedback, ' ELSE '' END || 
            '.' as api_content 
        FROM public.buz_operation_plan 
        WHERE bplan_id = {};
        """.format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_enhance_production = ''
        else:
            results = cur.fetchall()
            base_prompt = """You are a professional business writer. Create a concise business operations paragraph (approximately 50-100 words) that:
                            
                            1. Describes the integrated production enhancement strategies and comprehensive customer support framework
                            2. Uses formal third-person business language  
                            3. Highlights key production initiatives such as workforce development, technology upgrades, and process improvements alongside customer service pillars including post-purchase support and relationship management
                            4. Avoids list-like structures and repetitive phrasing
                            5. Emphasizes the dual commitment to operational excellence and complete customer satisfaction
                            6. Output a single, continuous paragraph only.
                            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results[0][0] }
                    ]
            result_enhance_production = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_enhance_production = result_enhance_production.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET buz_production = '{}', enhance_production = '{}' WHERE bplan_id = {};".format(chatgpt_buz_production, chatgpt_enhance_production ,bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_buz_distribution(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
        SELECT 
            CASE 
                WHEN type = 'Online' THEN 'Online distribution channel'
                WHEN type = 'Direct Sales' THEN 'Direct sales channel'
                WHEN type = 'Distributor' THEN 'Distributor name: ' || distribution_name
                WHEN type = 'Wholesaler' THEN 'Wholesaler name: ' || distribution_name
                WHEN type = 'Retailer' THEN 'Retailer name: ' || distribution_name
                ELSE 'Distribution channel: ' || distribution_name
            END || ' in charge of ' || type || ' with total collaboration years equals to ' || collaboration_years as api_content 
        FROM public.buz_distribution 
        WHERE bplan_id = {};
        """.format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_buz_distribution = ''
        else:
            results = []

            for row in cur.fetchall():
                results.append (row[0])

            results = ' and '.join(results)

            base_prompt = """You are a professional business writer. Create a comprehensive distribution network overview paragraph (approximately 100-150 words) that:

            1. Describes the company's multi-channel distribution strategy and partnerships
            2. Uses formal third-person business language
            3. Highlights the experience and longevity of distribution relationships
            4. Avoids list-like structures and repetitive phrasing
            5. Emphasizes the strength and reliability of the distribution network
            6. Presents the channels as an integrated, strategic advantage
            7. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."

            query_buz_distribution = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results }
                    ]
            result_buz_distribution = client.chat.completions.create(model=query_model, messages=query_buz_distribution)
            chatgpt_buz_distribution = result_buz_distribution.choices[0].message.content.replace("'", "''")

        sql = "SELECT 'The approaches used here to improve customer service includes : ' || CASE WHEN position('1' in customer_support)>0 THEN 'Return Policy, ' ELSE '' END || CASE WHEN position('2' in customer_support)>0 THEN 'Maintenance, ' ELSE '' END || CASE WHEN position('3' in customer_support)>0 THEN 'Warranty, ' ELSE '' END || CASE WHEN position('4' in customer_support)>0 THEN 'Customer Feedback, ' ELSE '' END || '.' as api_content FROM public.buz_operation_plan WHERE bplan_id = {};".format(bplan_id)
        cur.execute(sql)

        if cur.rowcount == 0:
            chatgpt_customer_support = ''
        else:
            results = cur.fetchall()
            base_prompt = """You are a professional business writer. Create a concise customer service enhancement strategies paragraph (approximately 50-100 words) that:

            1. Describes the comprehensive approaches to improve customer service and support
            2. Uses formal third-person business language
            3. Highlights key initiatives such as return policies, maintenance services, warranty programs, and feedback systems
            4. Avoids list-like structures and repetitive phrasing
            5. Emphasizes the commitment to customer satisfaction and continuous service improvement
            6. Presents these elements as an integrated customer experience strategy
            7. Output a single, continuous paragraph only.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                    {"role": "user", "content": base_prompt},
                    {"role": "user", "content": results[0][0] }
                    ]
            result_customer_support = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_customer_support = result_customer_support.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET buz_distribution = '{}', customer_support = '{}' WHERE bplan_id = {};".format(chatgpt_buz_distribution, chatgpt_customer_support, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_requested_fund(client, query_model, bplan_id, lang='en'):
    conn = None
    try:    
        db_params = config()   
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
                SELECT 
                    (
                        -- Project objectives
                        'The project objectives are ' ||
                        CASE WHEN position('1' in f.project_objectives) > 0 THEN 'Answering Increasing Market Need, ' ELSE '' END ||
                        CASE WHEN position('2' in f.project_objectives) > 0 THEN 'Developing Business Products, ' ELSE '' END ||
                        CASE WHEN position('3' in f.project_objectives) > 0 THEN 'Increasing Production Capacity, ' ELSE '' END ||
                        CASE WHEN position('4' in f.project_objectives) > 0 THEN 'Launching New Products, ' ELSE '' END ||
                        CASE WHEN position('5' in f.project_objectives) > 0 THEN 'Market Expansion, ' ELSE '' END ||
                        CASE WHEN position('6' in f.project_objectives) > 0 THEN 'Marketing & Promotion, ' ELSE '' END ||
                        CASE WHEN position('7' in f.project_objectives) > 0 THEN 'Opening a New Branch, ' ELSE '' END ||
                        '.' ||
                
                        -- Project purposes
                        ' The project purposes are ' ||
                        CASE WHEN position('1' in f.project_purposes) > 0 THEN 'Construction, ' ELSE '' END ||
                        CASE WHEN position('2' in f.project_purposes) > 0 THEN 'Electrical Work, ' ELSE '' END ||
                        CASE WHEN position('3' in f.project_purposes) > 0 THEN 'Equipment & Machinery, ' ELSE '' END ||
                        CASE WHEN position('4' in f.project_purposes) > 0 THEN 'Landscaping, ' ELSE '' END ||
                        CASE WHEN position('5' in f.project_purposes) > 0 THEN 'Marketing, ' ELSE '' END ||
                        CASE WHEN position('6' in f.project_purposes) > 0 THEN 'Mechanical Work, ' ELSE '' END ||
                        CASE WHEN position('7' in f.project_purposes) > 0 THEN 'Operation Cost, ' ELSE '' END ||
                        CASE WHEN position('8' in f.project_purposes) > 0 THEN 'Packing, ' ELSE '' END ||
                        CASE WHEN position('9' in f.project_purposes) > 0 THEN 'Raw Material, ' ELSE '' END ||
                        CASE WHEN position('10' in f.project_purposes) > 0 THEN 'Recruitment, ' ELSE '' END ||
                        CASE WHEN position('11' in f.project_purposes) > 0 THEN 'Renovation, ' ELSE '' END ||
                        CASE WHEN position('12' in f.project_purposes) > 0 THEN 'Rent, ' ELSE '' END ||
                        CASE WHEN position('13' in f.project_purposes) > 0 THEN 'Salaries, ' ELSE '' END ||
                        CASE WHEN position('14' in f.project_purposes) > 0 THEN 'Sub-Contracting Services, ' ELSE '' END ||
                        '.' ||
                
                        -- Fund type & details
                        ' The fund type is a ' || f.fund_type ||
                        ' for an amount of ' || f.amount ||
                        CASE 
                            WHEN f.fund_type = 'grant' THEN '.'
                            WHEN f.fund_type = 'investment' THEN 
                                ' with an equity equal to ' || f.equity || '%.'
                            WHEN f.fund_type = 'loan' THEN 
                                ' with an interest rate equal to ' || f.interest_rate || 
                                '% for a period of ' || f.period || 
                                ' years with a grace period of ' || f.grace_period || ' years.'
                            ELSE '' 
                        END ||
                
                        -- Project items (aggregated)
                        ' The project includes ' ||
                        COALESCE((
                            SELECT string_agg(
                                CASE 
                                    WHEN i.type_id = 1 THEN 
                                        'Installation costing ' || i.cost || ' per unit'
                                    WHEN i.type_id = 2 THEN 
                                        'Machinery & Equipment item "' || i.item || '" measured in ' || i.unit || 
                                        ' with a quantity of ' || i.quantity || 
                                        ' costing ' || i.cost || ' per unit' ||
                                        CASE WHEN i.quantity > 1 THEN ', giving a total cost of ' || i.total_cost ELSE '' END
                                    WHEN i.type_id = 3 THEN 
                                        'Raw Material item "' || i.item || '" measured in ' || i.unit || 
                                        ' with a quantity of ' || i.quantity || 
                                        ' costing ' || i.cost || ' per unit' ||
                                        CASE WHEN i.quantity > 1 THEN ', giving a total cost of ' || i.total_cost ELSE '' END
                                    WHEN i.type_id = 4 THEN 
                                        'Salaries item "' || i.item || '" measured in ' || i.unit || 
                                        ' with a quantity of ' || i.quantity || 
                                        ' costing ' || i.cost || ' per unit' ||
                                        CASE WHEN i.quantity > 1 THEN ', giving a total cost of ' || i.total_cost ELSE '' END
                                    WHEN i.type_id = 5 THEN 
                                        'Other Costs item "' || i.item || '" measured in ' || i.unit || 
                                        ' with a quantity of ' || i.quantity || 
                                        ' costing ' || i.cost || ' per unit' ||
                                        CASE WHEN i.quantity > 1 THEN ', giving a total cost of ' || i.total_cost ELSE '' END
                                    ELSE ''
                                END,
                                '; '
                            )
                            FROM public.buz_fund_items i
                            WHERE i.bplan_id = f.bplan_id
                        ), 'no listed items.') || '.'
                    ) AS api_content
                
                FROM public.buz_fund_details f
                WHERE f.bplan_id = {};
        """.format(bplan_id)
        cur.execute(sql)
        print(sql)

        if cur.rowcount == 0:
            chatgpt_requested_fund = ''
        else:
            results = cur.fetchone()[0]  # <-- Fetch single string result
            base_prompt = """You are a professional business writer. Create a concise, polished funding overview paragraph (approximately 150–300 words) for a business plan that:

            1. Interprets the provided project description into fluent, formal business English.
            2. Presents the project’s objectives, purposes, and funding details as a cohesive narrative.
            3. Highlights how the fund will be utilized across various cost categories (installation, equipment, salaries, etc.).
            4. Uses third-person, formal, and strategic language suitable for an investment or financing report.
            5. Avoids list-like structures, repetition, and direct enumeration.
            6. Emphasizes alignment between the funding allocation and the project’s overall development goals.
            7. **Do not include any titles, headings, or labels (e.g., “Funding Overview”).**
            8. Output a single, continuous paragraph only.

            Ensure the tone is confident, professional, and reads naturally for a business audience.
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
            if lang == "ar":
                base_prompt += " Do it in Arabic."
            query_messages = [
                {
                    "role": "user",
                    "content": base_prompt
                },
                {
                    "role": "user",
                    "content": results
                }
            ]

            result_requested_fund = client.chat.completions.create(model=query_model, messages=query_messages)
            chatgpt_requested_fund = result_requested_fund.choices[0].message.content.replace("'", "''")

        sql = "UPDATE public.buz_export_plan SET requested_fund = '{}' WHERE bplan_id = {};".format(chatgpt_requested_fund, bplan_id )
        cur.execute(sql)

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return (False, error )
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

def get_api_content_feasibility(client, query_model, bplan_id, lang='en'):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        # --- Get inflation rate ---
        inflation_data, _ = get_buz_inflation_rate(bplan_id)
        inflation_rate = float(inflation_data[0]['inflation_rate']) if inflation_data else 3.0

        data_buz_product = get_buz_product(bplan_id)[0] or []
        data_buz_expenses = get_buz_expenses(bplan_id)[0] or []


        # --- Calculate projections ---
        data_projections, data_total_projections = calculate_projections(
            data_buz_product,
            data_buz_expenses,
            inflation_rate=inflation_rate
        )


        # --- Get growth reasons data ---
        growth_reasons_data = []

        for product in data_buz_product:
            growth_reasons = {
                'product_name': product.get('product_service_name', ''),
                'year1': {
                    'percentage': float(product.get('growth_prct_year1')) if product.get(
                        'growth_prct_year1') is not None else None,
                    'reason': product.get('reason_of_growth_year1')
                },
                'year2': {
                    'percentage': float(product.get('growth_prct_year2')) if product.get(
                        'growth_prct_year2') is not None else None,
                    'reason': product.get('reason_of_growth_year2')
                },
                'year3': {
                    'percentage': float(product.get('growth_prct_year3')) if product.get(
                        'growth_prct_year3') is not None else None,
                    'reason': product.get('reason_of_growth_year3')
                },
                'year4': {
                    'percentage': float(product.get('growth_prct_year4')) if product.get(
                        'growth_prct_year4') is not None else None,
                    'reason': product.get('reason_of_growth_year4')
                },
                'year5': {
                    'percentage': float(product.get('growth_prct_year5')) if product.get(
                        'growth_prct_year5') is not None else None,
                    'reason': product.get('reason_of_growth_year5')
                }
            }

            # Debug print for each product's growth reasons
            product_name = product.get('product_service_name', 'Unknown')
            has_reasons = any(growth_reasons[year]['reason'] for year in ['year1', 'year2', 'year3', 'year4', 'year5'])
            print(f"DEBUG: Product '{product_name}' - Has growth reasons: {has_reasons}")

            if has_reasons:
                growth_reasons_data.append(growth_reasons)
                print(f"DEBUG: Added '{product_name}' to growth_reasons_data")


        # --- Format data for GPT ---
        import json
        from decimal import Decimal

        # Custom JSON encoder to handle Decimal objects
        class DecimalEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                return super(DecimalEncoder, self).default(obj)

        analysis_data = {
            'financial_projections': data_projections,
            'growth_drivers': growth_reasons_data
        }


        # Use custom encoder to handle Decimal objects
        projections_text = json.dumps(analysis_data, indent=2, cls=DecimalEncoder)
        base_prompt = """Write a financial feasibility analysis of the following projections. 
            Be professional, concise (around 150-200 words), and use third person pronouns.

            If growth drivers data is provided and exists, incorporate the specific growth reasons 
            (such as marketing efforts, new market entry, improved product quality, etc.) into the analysis 
            to explain the projected growth patterns.

            Focus on:
            1. Overall financial viability
            2. Key growth drivers and their credibility
            3. Risk factors based on the growth assumptions
            4. Sustainability of the projected growth
            You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content."""
        if lang == "ar":
            base_prompt += " Do it in Arabic."
        query_messages = [
            {"role": "user", "content": base_prompt},
            {"role": "user", "content": projections_text}
        ]
        result_feasibility = client.chat.completions.create(model=query_model, messages=query_messages)
        chatgpt_feasibility = result_feasibility.choices[0].message.content.replace("'", "''")



        # --- Save back to database ---
        sql = "UPDATE public.buz_export_plan SET feasibility = '{}' WHERE bplan_id = {};".format(chatgpt_feasibility,
                                                                                                 bplan_id)
        cur.execute(sql)

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"=== DEBUG: ERROR occurred: {error} ===")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")

# def get_api_content_buz_product_services(client, query_model, bplan_id):
#     conn = None
#     try:
#         db_params = config()
#         conn = psycopg2.connect(**db_params)
#         cur = conn.cursor()
#
#         # Step 1: Fetch product/services info
#         sql = """
#         SELECT 'Product/Service name: ' || product_service_name ||
#                ', Description: ' || COALESCE(product_service_description, 'No description')
#         AS api_content
#         FROM public.buz_product_services
#         WHERE bplan_id = %s;
#         """
#         cur.execute(sql, (bplan_id,))
#
#         if cur.rowcount == 0:
#             chatgpt_product_services = ''
#         else:
#             results = [row[0] for row in cur.fetchall()]
#             content_input = ' and '.join(results)
#
#             # Step 2: Generate description with ChatGPT
#             query_messages = [
#                 {"role": "user", "content": "Write a professional description of the products and services offered by this business in about 100 words using third-person perspective. Include the following information:"},
#                 {"role": "user", "content": content_input}
#             ]
#             result = client.chat.completions.create(model=query_model, messages=query_messages)
#             chatgpt_product_services = result.choices[0].message.content.replace("'", "''")
#
#         # Step 3: Update export plan
#         sql_update = """
#         UPDATE public.buz_export_plan
#         SET buz_product_services = %s
#         WHERE bplan_id = %s;
#         """
#         cur.execute(sql_update, (chatgpt_product_services, bplan_id))
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         return (False, error)
#     finally:
#         if conn is not None:
#             conn.commit()
#             conn.close()
#     return (True, "")




def generate_mission_vision_statements(client, query_model, bplan_id, lang='en'):
    """
    Generate mission and vision statements based on all previously generated business plan content
    """
    print(f"DEBUG: generate_mission_vision_statements started for bplan_id={bplan_id}")
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Get combined features only (simplified query from your working test)
        sql = """
        SELECT
            concat_ws(
                '',
                CASE WHEN complete_client_profile
                    THEN concat_ws('', client_profile, client_experiences, client_partners, client_expenses, client_employed, side_business)
                END,
                CASE WHEN complete_business_profile
                    THEN concat_ws('', business_profile, buz_staff, buz_resource, financial_history, source_of_funding)
                END,
                CASE WHEN complete_business_premises
                    THEN business_premises
                END,
                CASE WHEN complete_market_analysis
                    THEN market_analysis
                END,
                CASE WHEN complete_competitors
                    THEN client_experiences
                END,
                CASE WHEN complete_operations_plan
                    THEN concat_ws('', buz_suppliers, buz_production, enhance_production, buz_distribution, customer_support)
                END,
                CASE WHEN complete_requested_fund
                    THEN requested_fund
                END,
                CASE WHEN complete_feasibility
                    THEN feasibility
                END
            ) AS combined_features
        FROM public.buz_export_plan
        WHERE bplan_id = %s;
        """

        cur.execute(sql, (bplan_id,))
        result = cur.fetchone()

        if not result or not result[0]:
            print(f"DEBUG: No combined features found for bplan_id={bplan_id}")
            return (False, "No business plan content found to generate mission/vision")

        combined_features = result[0]
        print(f"DEBUG: Combined features length: {len(combined_features)}")

        # Construct prompt - JUST MISSION AND VISION (from your working test)
        base_prompt = """As an expert business strategist, analyze the COMPLETE business plan content below and create two comprehensive, professional sections. You MUST synthesize and incorporate ALL key elements from the provided content:

MISSION STATEMENT (1 paragraph, 80-100 words):
- Synthesize the core business purpose, target market, and value proposition
- Incorporate information about the business owner's background, experience, and qualifications
- Include relevant details about products/services, operations, and market positioning
- Reflect the current business activities and daily operations
- Use clear, actionable business language

VISION STATEMENT (1 paragraph, 80-100 words):
- Integrate the business's growth aspirations and long-term strategic direction
- Incorporate market analysis insights, competitive advantages, and expansion plans
- Include financial projections, funding requirements, and scalability potential
- Reflect operational enhancements, production capabilities, and distribution strategies
- Use inspirational, forward-looking language that shows ambition

CRITICAL REQUIREMENTS:
- You MUST analyze and incorporate ALL aspects of the provided business plan content
- Do not omit any major business elements mentioned in the content
- Ensure both mission and vision are comprehensive and reflect the full business scope
- Maintain professional, third-person business language throughout
- Output exactly two paragraphs with no additional commentary

Format your response EXACTLY as:
MISSION: [mission statement text here]
VISION: [vision statement text here]

You MUST ONLY use the information provided. DO NOT invent, add, or create anything that are not explicitly mentioned in the provided content.
Business Plan Content to analyze:"""

        if lang == "ar":
            base_prompt += " Do it in Arabic."

        full_content = combined_features
        print(f"DEBUG: Total content length for AI: {len(full_content)}")

        query_messages = [
            {"role": "user", "content": base_prompt},
            {"role": "user", "content": full_content}
        ]

        print("DEBUG: Calling OpenAI API...")
        try:
            result_mission_vision = client.chat.completions.create(model=query_model, messages=query_messages)
            generated_content = result_mission_vision.choices[0].message.content.replace("'", "''")
            print(f"DEBUG: Generated mission/vision content: {generated_content[:200]}...")

            # Parse the response
            mission = ""
            vision = ""

            if "MISSION:" in generated_content and "VISION:" in generated_content:
                mission = generated_content.split("MISSION:")[1].split("VISION:")[0].strip()
                vision = generated_content.split("VISION:")[1].strip()
            else:
                print("DEBUG: Response format not as expected, using fallback parsing")
                # Fallback: split by paragraphs
                paragraphs = [p.strip() for p in generated_content.split('\n\n') if p.strip()]
                if len(paragraphs) >= 2:
                    mission = paragraphs[0]
                    vision = paragraphs[1]
                else:
                    mission = generated_content

            print(f"DEBUG: Parsed - Mission: {len(mission)} chars, Vision: {len(vision)} chars")

            # Update the database with generated mission and vision
            update_sql = """
            UPDATE public.buz_export_plan 
            SET mission = %s, vision = %s
            WHERE bplan_id = %s;
            """
            cur.execute(update_sql, (mission, vision, bplan_id))
            print(f"DEBUG: Successfully updated mission and vision for bplan_id={bplan_id}")

        except Exception as e:
            print(f"ERROR: OpenAI call failed: {e}")
            return (False, str(e))

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: Database operation failed: {error}")
        return (False, error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return (True, "")


def get_api_content_objectives(client, query_model, bplan_id, lang='en'):
    """
    Generate AI content for business objectives using multiple objectives from bplan_objectives table.

    Args:
        client: OpenAI client instance
        query_model: Model to use for generation
        bplan_id: Business plan ID
        lang: Language code ('en' or 'ar')

    Returns:
        tuple: (success: bool, error_message: str)
    """
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Fetch all objectives from the new bplan_objectives table
        sql = """
            SELECT 
                objective_type,
                objective_strategy,
                objective_target,
                objective_timeline,
                objective_unit,
                objective_order
            FROM public.bplan_objectives
            WHERE bplan_id = %s
            ORDER BY objective_order ASC;
        """
        cur.execute(sql, (bplan_id,))
        objectives_rows = cur.fetchall()

        # If no objectives in new table, fall back to bplan table for backward compatibility
        if not objectives_rows:
            sql_fallback = """
                SELECT 
                    objective_type,
                    objective_strategy,
                    objective_target,
                    objective_timeline,
                    objective_unit,
                    1 as objective_order
                FROM public.bplan
                WHERE bplan_id = %s
                    AND objective_type IS NOT NULL 
                    AND objective_type != '';
            """
            cur.execute(sql_fallback, (bplan_id,))
            objectives_rows = cur.fetchall()

        if not objectives_rows:
            chatgpt_objectives = ''
        else:
            # Build objective sentences for each objective
            objective_sentences = []

            for row in objectives_rows:
                obj_type = row[0]
                obj_strategy = row[1]
                obj_target = row[2]
                obj_timeline = row[3]
                obj_unit = row[4]
                obj_order = row[5]

                if not obj_type:
                    continue

                # Build the sentence based on objective type
                if obj_type == 'Enhance customer satisfaction':
                    # Customer satisfaction doesn't have numeric targets
                    sentence = f"The business objective is to {obj_type.lower()} by {obj_strategy.lower() if obj_strategy else 'improving service quality'}"
                else:
                    # Other objectives have numeric targets
                    # Handle pluralization for time units
                    unit_str = obj_unit.lower() if obj_unit else 'month'
                    if obj_timeline and int(obj_timeline) > 1:
                        unit_str += 's'

                    # Build the full sentence
                    target_str = f"{obj_target}%" if obj_target else "a significant amount"
                    timeline_str = f"{obj_timeline} {unit_str}" if obj_timeline and obj_unit else "the planned period"
                    strategy_str = obj_strategy.lower() if obj_strategy else "strategic initiatives"

                    sentence = f"The business objective is to {obj_type.lower()} by {target_str} over {timeline_str} through {strategy_str}"

                objective_sentences.append(sentence)

            # Join all objectives
            if len(objective_sentences) == 1:
                combined_objectives = objective_sentences[0]
            elif len(objective_sentences) == 2:
                combined_objectives = ' and '.join(objective_sentences)
            else:
                # For 3+ objectives: "obj1, obj2, and obj3"
                combined_objectives = ', '.join(objective_sentences[:-1]) + ', and ' + objective_sentences[-1]

            # Build the prompt based on number of objectives
            num_objectives = len(objective_sentences)

            base_prompt = f"""You are a professional business writer. Create a concise strategic objectives paragraph (approximately {100 + (num_objectives - 1) * 50}-{150 + (num_objectives - 1) * 50} words) that:
                
                1. Describes ALL {num_objectives} business objective{'s' if num_objectives > 1 else ''} provided - DO NOT ADD any additional objectives, percentages, or targets
                2. Uses formal third-person business language
                3. Highlights the measurable targets and implementation strategies EXACTLY as provided
                4. {'Connects the multiple objectives cohesively, showing how they work together' if num_objectives > 1 else 'Presents the objective clearly and professionally'}
                5. Avoids list-like structures and repetition
                6. Emphasizes growth, innovation, and business development
                7. Output a single, continuous paragraph only
                
                CRITICAL: You MUST ONLY use the {num_objectives} objective{'s' if num_objectives > 1 else ''} information provided. DO NOT invent, add, or create any new objectives, percentages, targets, or strategies that are not explicitly mentioned in the provided content."""

            # Language instruction
            if lang == "ar":
                base_prompt += "\n\nWrite the entire response in Arabic language. Use ONLY the provided objectives - do not add any new information."
            else:
                base_prompt += "\n\nWrite the entire response in English language. Use ONLY the provided objectives - do not add any new information."

            query_messages = [
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": combined_objectives}
            ]

            # API call with error handling
            try:
                result_objectives = client.chat.completions.create(
                    model=query_model,
                    messages=query_messages
                )
                if result_objectives.choices and len(result_objectives.choices) > 0:
                    chatgpt_objectives = result_objectives.choices[0].message.content.replace("'", "''")
                else:
                    chatgpt_objectives = "Error: No response from AI API"
            except Exception as api_error:
                print(f"API Error: {api_error}")
                return (False, f"API call failed: {str(api_error)}")

        # Update the export plan with generated content
        update_sql = "UPDATE public.buz_export_plan SET objectives = %s WHERE bplan_id = %s;"
        cur.execute(update_sql, (chatgpt_objectives, bplan_id))

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database Error: {error}")
        return (False, str(error))
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

    return (True, "")
def get_formatted_objectives(bplan_id):
    """
    Get all objectives for a business plan formatted for display.

    Args:
        bplan_id: Business plan ID

    Returns:
        list: List of formatted objective dictionaries
    """
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """
            SELECT 
                objective_id,
                objective_order,
                objective_type,
                objective_strategy,
                objective_target,
                objective_timeline,
                objective_unit
            FROM public.bplan_objectives
            WHERE bplan_id = %s
            ORDER BY objective_order ASC;
        """
        cur.execute(sql, (bplan_id,))
        rows = cur.fetchall()

        objectives = []
        for row in rows:
            obj = {
                'id': row[0],
                'order': row[1],
                'type': row[2],
                'strategy': row[3],
                'target': float(row[4]) if row[4] else None,
                'timeline': int(row[5]) if row[5] else None,
                'unit': row[6],
                'formatted': format_single_objective(row[2], row[3], row[4], row[5], row[6])
            }
            objectives.append(obj)

        cur.close()
        return objectives

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database Error: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()
def format_single_objective(obj_type, obj_strategy, obj_target, obj_timeline, obj_unit):
    """
    Format a single objective into a readable string.

    Returns:
        str: Formatted objective string
    """
    if not obj_type:
        return ""

    if obj_type == 'Enhance customer satisfaction':
        return f"{obj_type} through {obj_strategy}" if obj_strategy else obj_type
    else:
        parts = [obj_type]

        if obj_target:
            parts.append(f"by {obj_target}%")

        if obj_timeline and obj_unit:
            unit_str = obj_unit.lower()
            if int(obj_timeline) > 1:
                unit_str += 's'
            parts.append(f"in {obj_timeline} {unit_str}")

        if obj_strategy:
            parts.append(f"via {obj_strategy}")

        return ' '.join(parts)
def get_objectives_summary(bplan_id, lang='en'):
    """
    Get a summary of all objectives for use in reports.

    Args:
        bplan_id: Business plan ID
        lang: Language code ('en' or 'ar')

    Returns:
        dict: Summary with count and list of objectives
    """
    objectives = get_formatted_objectives(bplan_id)

    # Translations for objective types
    type_translations = {
        'Increase profitability': 'زيادة الربحية',
        'Increase sales': 'زيادة المبيعات',
        'Enhance Production Capacity': 'تعزيز الطاقة الإنتاجية',
        'Increase market share': 'زيادة الحصة السوقية',
        'Enhance customer satisfaction': 'تعزيز رضا العملاء'
    }

    unit_translations = {
        'Week': 'أسبوع',
        'Month': 'شهر',
        'Year': 'سنة'
    }

    if lang == 'ar':
        for obj in objectives:
            obj['type_display'] = type_translations.get(obj['type'], obj['type'])
            obj['unit_display'] = unit_translations.get(obj['unit'], obj['unit'])
    else:
        for obj in objectives:
            obj['type_display'] = obj['type']
            obj['unit_display'] = obj['unit']

    return {
        'count': len(objectives),
        'objectives': objectives,
        'has_objectives': len(objectives) > 0
    }

@blueprint.route('/global-dashboard')
@login_required
def global_dashboard():
    return render_template('home/global_dashboard.html', segment='global_dashboard')

@blueprint.route('/assessments')
@login_required
def assessments():
    return render_template('home/assessments.html', segment='assessments')

@blueprint.route('/reports')
@login_required
def reports():
    return render_template('home/reports.html', segment='reports')

@blueprint.route('/index')
@login_required
def index():
    # Check if it's an AJAX delete request
    delete_id = request.args.get('delete')
    if delete_id and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX delete - Use the comprehensive delete function
        try:
            result = delete_bplan_complete(delete_id)

            # Check if deletion was successful
            if "successfully" in result.lower() or "تم" in result:
                return jsonify({'success': True, 'message': result})
            else:
                return jsonify({'success': False, 'message': result})

        except Exception as error:
            print(f"AJAX delete error: {error}")
            if session.get('lang', 'en') == 'ar':
                message = 'حدث خطأ أثناء حذف خطة العمل'
            else:
                message = 'Error occurred while deleting business plan'
            return jsonify({'success': False, 'message': f"{message}: {str(error)}"})

    # Normal page load
    results, status = get_bplan_list()
    if '*' in results:
        return render_template('accounts/login.html', msg=status)
    else:
        return render_template('home/index.html', segment='index', data=results)




@blueprint.route('/set-language/<lang>')
@login_required  # Add this if you want it protected
def set_language(lang):
    if lang in ['en', 'ar']:
        session['lang'] = lang
    # Redirect back to the previous page
    return redirect(request.referrer or url_for('home_blueprint.index'))


@blueprint.route('/new_plan', methods=['GET', 'POST'])
@login_required
def new_plan():
    if request.method == 'POST':
        if request.form.get('option') == 'create':
            print('Creating new business plan')

            # Get the objectives JSON from the form
            objectives_json = request.form.get('objectives_json', '[]')

            try:
                objectives = json.loads(objectives_json)
            except json.JSONDecodeError:
                objectives = []

            # Insert the business plan with multiple objectives support
            result = insert_bplan_with_objectives(
                var_name=request.form.get('brand_name'),
                var_industry=request.form.get('choices_industry'),
                var_sector=request.form.get('choices_sector'),
                var_subsector=request.form.get('choices_subsector'),
                var_currency=request.form.get('choices_currency'),
                var_status=request.form.get('choices_status'),
                objectives=objectives  # Pass the list of objectives
            )

            if result == "Insertion successful":
                return redirect(url_for('home_blueprint.index'))
            else:
                # Handle error - you might want to show an error message
                print(f"Error creating plan: {result}")
                return redirect(url_for('home_blueprint.index'))

        elif request.form.get('option') == 'cancel':
            return redirect(url_for('home_blueprint.index'))

    # GET method (show form)
    data_lst_industries, status_lst_industries = get_lst_industries()
    data_lst_sectors, status_sectors = get_lst_sectors()

    if '*' in data_lst_industries or '*' in data_lst_sectors:
        return render_template('accounts/login.html', msg=status_lst_industries)

    # Get current language from session
    current_lang = session.get('lang', 'en')

    return render_template('home/newplan.html',
                           lst_industries=data_lst_industries,
                           lst_sectors=data_lst_sectors,
                           current_lang=current_lang)


@blueprint.route('/clientprofile/<bplan_id>', methods=['GET', 'POST'])
@login_required
def clientprofile(bplan_id):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # ============================================================
        # SILENT SAVE - Save client info without redirect (for AJAX)
        # This is called before adding items to tables to prevent data loss
        # ============================================================
        if request.form.get('silent_save'):
            _save_client_info(bplan_id, request)
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # ============================================================
        # TABLE OPERATIONS (AJAX) - Handle these and return page
        # ============================================================

        # --- Partners DELETE ---
        if request.form.get('partner_delete'):
            partner_delete(request.form.get('partner_delete'))
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # --- Partners ADD ---
        if request.form.get('partner_add'):
            partner_add(
                request.form.get('partner_add'),
                request.form.get('partner_name'),
                request.form.get('choice_partner_relation'),
                request.form.get('partner_experience'),
                request.form.get('partner_years_of_experience'),
                request.form.get('partner_role'),
                request.form.get('partner_shares')
            )
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # --- Experiences DELETE ---
        if request.form.get('experience_delete'):
            experience_delete(request.form.get('experience_delete'))
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # --- Experiences ADD ---
        if request.form.get('experiences_add'):
            experiences_add(
                request.form.get('experiences_add'),
                request.form.get('experience_field'),
                request.form.get('years_of_experience'),
                request.form.get('experience_workplace')
            )
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # --- Expenses DELETE ---
        if request.form.get('expense_delete'):
            client_profile_expense_delete(request.form.get('expense_delete'))
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # --- Expenses ADD ---
        if request.form.get('expenses_add'):
            expenses_add(
                request.form.get('expenses_add'),
                request.form.get('choices_living_expenses'),
                request.form.get('expense_value'),
                request.form.get('choice_expense_unit')
            )
            if is_ajax:
                return _render_clientprofile_page(bplan_id)

        # ============================================================
        # FULL FORM SUBMISSION (Save button) - Save everything
        # ============================================================

        # Save all client information
        _save_client_info(bplan_id, request)

        # If save button clicked, update completion and redirect
        if request.form.get('action') == "save":
            update_bplan_completion('complete_client_profile', bplan_id)
            return redirect(url_for('home_blueprint.bussiness_profile', bplan_id=bplan_id))

        # Default redirect after POST to prevent resubmission
        return redirect(url_for('home_blueprint.clientprofile', bplan_id=bplan_id))

    # --- GET request: load all data ---
    return _render_clientprofile_page(bplan_id)


def _save_client_info(bplan_id, request):
    """
    Helper function to save all client profile information.
    Extracted to avoid code duplication between silent_save and full save.
    """
    # --- Load existing client info to preserve avatar ---
    data_client_info, status_client_info = get_client_profile(bplan_id)
    current_avatar = (
        data_client_info[0].get('client_avatar', 'avatar.png')
        if data_client_info and len(data_client_info) > 0
        else 'avatar.png'
    )

    # --- Employed info ---
    if request.form.get('flexSwitchCheck_employed') is None:
        update_employed('', '', '', '', 0, bplan_id)
    else:
        update_employed(
            request.form.get('employed_where') or '',
            request.form.get('employed_job_hold') or '',
            request.form.get('employed_location') or '',
            request.form.get('employed_duration') or '',
            request.form.get('employed_monthly_income') or 0,
            bplan_id
        )

    # --- Side business info ---
    if request.form.get('flexSwitchCheck_business') is None:
        update_side_business('', 0, '', '', 0, bplan_id)
    else:
        update_side_business(
            request.form.get('business_name') or '',
            request.form.get('choices_industry') or 0,
            request.form.get('business_location') or '',
            request.form.get('business_duration') or '',
            request.form.get('business_monthly_income') or 0,
            bplan_id
        )

    # --- Avatar logic (preserve old if no new file uploaded) ---
    file = request.files.get('fileAvatar')
    if file and file.filename and allowed_file(file.filename):
        filename = f"{bplan_id}.{file.filename.rsplit('.', 1)[1].lower()}"
        file.save(os.path.join('apps/static/uploads', filename))
    else:
        filename = current_avatar

    # --- Update profile fields ---
    update_client_profile(
        request.form.get('full_name') or '',
        filename,
        request.form.get('choice_gender') or 'Male',
        request.form.get('choice_status') or 'Single',
        request.form.get('number_of_children') or 0,
        request.form.get('choice_nationality') or '',
        request.form.get('date_of_birth') or '2000-01-01',
        request.form.get('choice_education_level') or 'Bachelor',
        request.form.get('years_experience') or 0,
        request.form.get('education_major') or '',
        request.form.get('specialty') or '',
        request.form.get('education_institution') or '',
        bplan_id
    )


def _render_clientprofile_page(bplan_id):
    """
    Helper function to render the client profile page with all required data.
    """
    data_completion, status_completion = get_completion(bplan_id)
    data_client_info, status_client_info = get_client_profile(bplan_id)
    data_partners, status_partners = get_partners(bplan_id)
    data_experiences, status_experiences = get_experiences(bplan_id)
    status_expenses, data_expenses, total_expenses = get_expenses(bplan_id)
    data_employed, status_employed = get_employed(bplan_id)
    data_side_business, status_side_business = get_side_business(bplan_id)
    data_lst_nationalities, status_lst_nationalities = get_lst_nationalities()
    data_lst_industries, status_lst_industries = get_lst_industries()

    return render_template(
        'home/clientprofile.html',
        segment='clientprofile',
        data_comp=data_completion,
        data_ci=data_client_info,
        data_p=data_partners,
        data_e=data_experiences,
        data_x=data_expenses,
        data_x_total=total_expenses,
        data_emp=data_employed,
        data_buz=data_side_business,
        lst_nationalities=data_lst_nationalities,
        lst_industries=data_lst_industries,
        bplan_id=bplan_id
    )

@blueprint.route('/business_profile/<bplan_id>', methods=['GET', 'POST'])
@login_required
def bussiness_profile(bplan_id):

    if request.method == 'POST':
        update_bool = False

        if request.form.get('product_service_add') is not None:
            update_bool = True
            product_service_add(
                bplan_id,
                request.form.get('product_service_name'),
                request.form.get('product_service_description'),
                request.form.get('product_service_image')  # or file/image handler if applicable
            )

        if request.form.get('product_service_delete') is not None:
            update_bool = True
            delete_product_service(request.form.get('product_service_delete'))


        if request.form.get('staff_add') != None:
            update_bool = True
            staff_add(  request.form.get('staff_add'),
                        request.form.get('staff_position'),
                        request.form.get('choice_work_time'),
                        request.form.get('staff_salary') )
        if request.form.get('staff_delete') != None:
            update_bool = True
            staff_delete(request.form.get('staff_delete'))
        if request.form.get('resource_add') != None:
            update_bool = True
            resource_add(   request.form.get('resource_add') ,
                            request.form.get('choice_type'),
                            request.form.get('choice_subtype'),
                            request.form.get('resource_value'))
        if request.form.get('resource_delete') != None:
            update_bool = True
            resource_delete(request.form.get('resource_delete'))
        if request.form.get('financial_add') != None:
            update_bool = True
            financial_add(request.form.get('financial_add'),
                          request.form.get('financial_year'),
                          request.form.get('financial_sales'),
                          request.form.get('financial_profit'))
        if request.form.get('financial_delete') != None:
            update_bool = True
            financial_delete(request.form.get('financial_delete'))
        if request.form.get('fund_add') != None:
            update_bool = True
            other_resource_add(request.form.get('fund_add'),
                               request.form.get('choice_fund') ,
                               request.form.get('fund_contribution') )
        if request.form.get('fund_delete') != None:
            update_bool = True
            other_resource_delete(request.form.get('fund_delete') )

        if update_bool:
            update_buz_info(    request.form.get('buz_address'),
                                request.form.get('buz_est_date'),
                                request.form.get('choice_legal_status'),
                                str(request.form.getlist('choice_business_model')).replace("'", ""),
                                request.form.get('product_services'),
                                bplan_id)


        # ✅ ADD THIS AJAX DETECTION RIGHT BEFORE THE REDIRECT:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return full page for AJAX requests
            data_completion, status_completion = get_completion(bplan_id)
            data_buz_info, status_buz_info = get_buz_info(bplan_id)
            status_buz_staff, data_buz_staff, data_buz_total_salaries = get_buz_staff(bplan_id)
            status_buz_resource, data_buz_resource, data_buz_total_resources = get_buz_resource(bplan_id)
            data_buz_financial, status_buz_financial = get_buz_financial(bplan_id)
            data_buz_other_resource, status_buz_other_resource = get_buz_other_resource(bplan_id)
            status_buz_product_services, data_buz_product_services = get_product_services(bplan_id)

            return render_template('home/businessprofile.html', segment='businessprofile',
                                   data_comp = data_completion,
                                   data_bi = data_buz_info,
                                   data_bs = data_buz_staff,
                                   data_bs_total = data_buz_total_salaries,
                                   data_br = data_buz_resource,
                                   data_br_total = data_buz_total_resources,
                                   data_fin = data_buz_financial,
                                   data_bor = data_buz_other_resource,
                                   data_bps = data_buz_product_services,
                                   bplan_id = bplan_id)

        if request.form.get('action') == 'save':
            update_bplan_completion ('complete_business_profile',bplan_id)
            update_buz_info(    request.form.get('buz_address'),
                                request.form.get('buz_est_date'),
                                request.form.get('choice_legal_status'),
                                str(request.form.getlist('choice_business_model')).replace("'", ""),
                                request.form.get('product_services'),
                                bplan_id)
            return redirect(url_for('home_blueprint.business_premises', bplan_id=bplan_id))
        # ✅ Redirect after any POST to prevent duplicate insertions on refresh
        return redirect(url_for('home_blueprint.bussiness_profile', bplan_id=bplan_id))

    data_completion, status_completion = get_completion(bplan_id)
    data_buz_info, status_buz_info = get_buz_info(bplan_id)
    status_buz_staff, data_buz_staff, data_buz_total_salaries = get_buz_staff(bplan_id)
    status_buz_resource, data_buz_resource, data_buz_total_resources = get_buz_resource(bplan_id)
    data_buz_financial, status_buz_financial = get_buz_financial(bplan_id)
    data_buz_other_resource, status_buz_other_resource = get_buz_other_resource(bplan_id)
    status_buz_product_services, data_buz_product_services = get_product_services(bplan_id)

    return render_template('home/businessprofile.html', segment='businessprofile',
                           data_comp = data_completion,
                           data_bi = data_buz_info,
                           data_bs = data_buz_staff,
                           data_bs_total = data_buz_total_salaries,
                           data_br = data_buz_resource,
                           data_br_total = data_buz_total_resources,
                           data_fin = data_buz_financial,
                           data_bor = data_buz_other_resource,
                           data_bps=data_buz_product_services,  # <- NEW Youssef
                           bplan_id = bplan_id)


def allowed_doc(filename):
    # Added jpg, jpeg, png, webp
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions



def premises_doc_add(bplan_id, filename, description=None):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = """INSERT INTO public.buz_premises_doc (bplan_id, premises_doc_filename, description)
                 VALUES (%s, %s, %s)"""
        cur.execute(sql, (bplan_id, filename, description))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error inserting document:", error)
    finally:
        if conn is not None:
            conn.close()

@blueprint.route('/upload_doc_temp/<bplan_id>', methods=['POST'])
def upload_doc_temp(bplan_id):
    """Upload document to temporary storage"""
    if 'file' not in request.files:
        return {'error': 'No file uploaded'}, 400

    file = request.files['file']
    if not file or file.filename == '':
        return {'error': 'No file selected'}, 400

    if not allowed_doc(file.filename):
        return {'error': 'File type not allowed'}, 400

    try:
        # Get original filename and create secure version
        original_filename = file.filename
        filename = secure_filename(original_filename)

        # Create TEMP directory
        temp_path = os.path.join('apps', 'static', 'uploads', 'docs', 'temp', str(bplan_id))
        os.makedirs(temp_path, exist_ok=True)

        # Generate unique filename
        base_name, ext = os.path.splitext(filename)
        unique_filename = filename
        counter = 1

        while os.path.exists(os.path.join(temp_path, unique_filename)):
            unique_filename = f"{base_name}_{counter}{ext}"
            counter += 1
            if counter > 100:
                return {'error': 'Too many files with similar names'}, 500

        # Save to TEMP location
        full_path = os.path.join(temp_path, unique_filename)
        file.save(full_path)

        if not os.path.exists(full_path):
            return {'error': 'File was not saved properly'}, 500

        print(f"File saved to temp: {full_path}")

        # DON'T save to database yet - wait for save_doc
        return {
            'message': 'Document uploaded successfully',
            'filename': unique_filename
        }, 200

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {'error': f'Error saving document: {str(e)}'}, 500


@blueprint.route('/save_doc/<bplan_id>', methods=['POST'])
def save_doc(bplan_id):
    filename = request.form.get('filename')
    description = request.form.get('description', '')

    if not filename:
        return {'error': 'No filename provided'}, 400

    try:
        temp_path = f'apps/static/uploads/docs/temp/{bplan_id}'
        permanent_path = f'apps/static/uploads/docs/{bplan_id}'
        os.makedirs(permanent_path, exist_ok=True)

        temp_file = os.path.join(temp_path, filename)
        final_file = os.path.join(permanent_path, filename)

        # Move file from temp to permanent
        if os.path.exists(final_file):
            print("File already exists in permanent folder — skipping move.")
        elif os.path.exists(temp_file):
            os.rename(temp_file, final_file)
        else:
            print("File not found in temp or permanent folder")
            return {'error': 'File not found'}, 404

        # Check if record already exists and get doc_id
        conn = psycopg2.connect(**config())
        cur = conn.cursor()
        cur.execute("""
            SELECT doc_id FROM buz_premises_doc 
            WHERE bplan_id=%s AND premises_doc_filename=%s
        """, (bplan_id, filename))
        existing = cur.fetchone()

        doc_id = None
        if existing:
            doc_id = existing[0]
            # Update description if it exists
            cur.execute("""
                UPDATE buz_premises_doc 
                SET description=%s 
                WHERE doc_id=%s
            """, (description, doc_id))
            conn.commit()
        else:
            # Insert new record and get the doc_id
            cur.execute("""
                INSERT INTO buz_premises_doc (bplan_id, premises_doc_filename, description)
                VALUES (%s, %s, %s)
                RETURNING doc_id
            """, (bplan_id, filename, description))
            doc_id = cur.fetchone()[0]
            conn.commit()

        cur.close()
        conn.close()

        return {
            'message': 'Document saved successfully',
            'filename': filename,
            'description': description,
            'doc_id': doc_id
        }, 200

    except Exception as e:
        print(f"Save error: {e}")
        return {'error': f'Error saving document: {str(e)}'}, 500


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/upload/<bplan_id>', methods=['POST'])
def upload_file(bplan_id):
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Here to save the file
            try:
                newpath = 'apps/static/uploads/' + bplan_id
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                file.save(os.path.join(newpath, filename))
                premises_photo_add(bplan_id, filename)
                # file.save(os.path.join('path_to_your_upload_folder', filename))
            except Exception as e:
                return f'Error saving file: {str(e)}', 500

            return redirect(url_for('home_blueprint.business_premises', bplan_id=bplan_id))

    return 'No file uploaded'


@blueprint.route('/business_premises/<bplan_id>', methods=['GET', 'POST'])
@login_required
def business_premises(bplan_id):
    import ast

    if request.method == 'POST':

        if "delete_photo" in request.form:
            photo_ids = request.form.getlist("photo_to_delete")  # ✅ Gets ALL selected values
            for photo_id in photo_ids:
                premises_photo_delete(photo_id)
            return redirect(url_for('home_blueprint.business_premises', bplan_id=bplan_id))

        if "delete_doc" in request.form:
            doc_ids = request.form.getlist("doc_to_delete")  # Use getlist for multiple checkboxes
            for doc_id in doc_ids:
                premises_doc_delete(doc_id)
            return redirect(url_for('home_blueprint.business_premises', bplan_id=bplan_id))

        if request.form.get('premise_add') != None:
            premise_add(request.form.get('premise_add'),
                        request.form.get('premise_address'),
                        request.form.get('plot_number'),
                        ', '.join(map(str, request.form.getlist('choice_premise_nature'))),
                        # request.form.get('choice_premise_nature'),
                        request.form.get('plot_area'),
                        request.form.get('choice_premises_ownershipe'),
                        ', '.join(map(str, request.form.getlist('choice_surroundings'))),
                        request.form.get('partner_name'),
                        request.form.get('partner_relation'),
                        request.form.get('percentge_of_ownership'),
                        request.form.get('rent_fees'),
                        request.form.get('rent_period'),
                        request.form.get('choice_rent_unit')
                        )

        if request.form.get('premise_delete') != None:
            premise_delete(request.form.get('premise_delete'))

        if request.form.get('action') == 'save':
            update_bplan_completion('complete_business_premises', bplan_id)
            return redirect(url_for('home_blueprint.market_analysis', bplan_id=bplan_id))

        # ✅ ONLY ADD THIS CHECK AT THE VERY END OF YOUR POST HANDLING:
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return the full page but AJAX will extract just the table
            data_buz_premise, status_buz_premise = get_buz_premise(bplan_id)
            data_completion, status_completion = get_completion(bplan_id)
            data_buz_premises_photo, status_buz_premises_photo = get_buz_premises_photo(bplan_id)
            data_buz_premises_doc, status_buz_premises_doc = get_buz_premises_doc(bplan_id)

            return render_template('home/businesspremises.html', segment='businesspremises',
                                   data_comp=data_completion,
                                   data_bp=data_buz_premise,
                                   data_bp_photo=data_buz_premises_photo,
                                   data_bp_doc=data_buz_premises_doc,
                                   bplan_id=bplan_id)
        # ✅ Redirect after any POST to prevent duplicate insertions on refresh
        return redirect(url_for('home_blueprint.business_premises', bplan_id=bplan_id))


    data_completion, status_completion = get_completion(bplan_id)
    data_buz_premise, status_buz_premise = get_buz_premise(bplan_id)
    data_buz_premises_photo, status_buz_premises_photo = get_buz_premises_photo(bplan_id)
    data_buz_premises_doc, status_buz_premises_doc = get_buz_premises_doc(bplan_id)
    # In your route, before rendering template:
    print("Documents data:", data_buz_premises_doc)
    for doc in data_buz_premises_doc:
        print("Doc:", doc.__dict__ if hasattr(doc, '__dict__') else doc)


    return render_template('home/businesspremises.html', segment='businesspremises',
                           data_comp=data_completion,
                           data_bp=data_buz_premise,
                           data_bp_photo=data_buz_premises_photo,
                           data_bp_doc=data_buz_premises_doc,
                           bplan_id=bplan_id)


@blueprint.route('/add_b2b_client/<bplan_id>/<segment_id>', methods=['POST'])
@login_required
def add_b2b_client_route(bplan_id, segment_id):
    """AJAX endpoint to add B2B client"""
    try:
        data = request.get_json()
        client_name = data.get('client_name', '').strip()
        client_location = data.get('client_location', '').strip()
        client_description = data.get('client_description', '').strip()

        if not client_name or not client_location:
            return jsonify({'success': False, 'error': 'Name and location are required'}), 400

        client_id = add_b2b_client(bplan_id, segment_id, client_name, client_location, client_description)

        if client_id:
            return jsonify({
                'success': True,
                'client': {
                    'client_id': client_id,
                    'client_name': client_name,
                    'client_location': client_location,
                    'client_description': client_description
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to add client'}), 500

    except Exception as e:
        print(f"Error in add_b2b_client_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route('/delete_b2b_client/<client_id>', methods=['POST'])
@login_required
def delete_b2b_client_route(client_id):
    """AJAX endpoint to delete B2B client"""
    try:
        delete_b2b_client(client_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error in delete_b2b_client_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route('/market_analysis/<bplan_id>', methods=['GET', 'POST'])
@login_required
def market_analysis(bplan_id):

    import ast

    if request.method == 'POST':
        age_range_status = "on" if request.form.get('show_age_range') == 'on' else "off"
        if request.form.get('action') == "save":
            update_bplan_completion ('complete_market_analysis',bplan_id)

            # Get all switch values from the form
            show_age_range = "on" if request.form.get('show_age_range') == 'on' else "off"
            show_income_range = "on" if request.form.get('show_income_range') == 'on' else "off"
            show_gender_percentage = "on" if request.form.get('show_gender_percentage') == 'on' else "off"
            show_education = "on" if request.form.get('show_education') == 'on' else "off"
            show_occupation = "on" if request.form.get('show_occupation') == 'on' else "off"
            show_life_stage = "on" if request.form.get('show_life_stage') == 'on' else "off"

            # Call the function with all switches
            update_buz_mkt_analysis(
                request.form.get('segment_name'),
                request.form.get('choice_business_model'),
                request.form.get('segment_percentage'),
                str(request.form.getlist('choice_marketing_channel')).replace("'", ""),
                request.form.get('sliderAge_min'), request.form.get('sliderAge_max'),
                request.form.get('sliderIncome_min'), request.form.get('sliderIncome_max'),
                request.form.get('sliderGender_male'), request.form.get('sliderGender_female'),
                str(request.form.getlist('choice_education')).replace("'", ""),
                str(request.form.getlist('choice_occupation')).replace("'", ""),
                str(request.form.getlist('choice_life_stage')).replace("'", ""),
                request.form.get('b2c_location'),
                request.form.get('b2b_location'),
                request.form.get('preferences'),
                request.form.get('choices_industry'),
                request.form.get('segment_company_size'),
                show_age_range, show_income_range, show_gender_percentage, show_education, show_occupation,
                show_life_stage,
                bplan_id,
                request.form.get('mkt_segment_id')
            )

            data_price_preferences, status_price_preferences = get_preferences (bplan_id, '1', False)
            data_service_preferences, status_service_preferences = get_preferences (bplan_id, '2', False)
            data_quality_preferences, status_quality_preferences = get_preferences (bplan_id, '3', False)
            data_location_preferences, status_location_preferences = get_preferences (bplan_id, '4', False)
            
            for data in data_price_preferences: update_buz_preferences( bplan_id, data['preference'], request.form.get(data['preference']))
            for data in data_service_preferences: update_buz_preferences( bplan_id, data['preference'], request.form.get(data['preference']))
            for data in data_quality_preferences: update_buz_preferences( bplan_id, data['preference'], request.form.get(data['preference']))
            for data in data_location_preferences: update_buz_preferences( bplan_id, data['preference'], request.form.get(data['preference']))

            return redirect(url_for('home_blueprint.competitors', bplan_id=bplan_id ))

        if request.form.get('action') == "Save_segment":
            # Get all switch values from the form
            show_age_range = "on" if request.form.get('show_age_range') == 'on' else "off"
            show_income_range = "on" if request.form.get('show_income_range') == 'on' else "off"
            show_gender_percentage = "on" if request.form.get('show_gender_percentage') == 'on' else "off"
            show_education = "on" if request.form.get('show_education') == 'on' else "off"
            show_occupation = "on" if request.form.get('show_occupation') == 'on' else "off"
            show_life_stage = "on" if request.form.get('show_life_stage') == 'on' else "off"

            # Call the function with all switches
            update_buz_mkt_analysis(
                request.form.get('segment_name'),
                request.form.get('choice_business_model'),
                request.form.get('segment_percentage'),
                str(request.form.getlist('choice_marketing_channel')).replace("'", ""),
                request.form.get('sliderAge_min'), request.form.get('sliderAge_max'),
                request.form.get('sliderIncome_min'), request.form.get('sliderIncome_max'),
                request.form.get('sliderGender_male'), request.form.get('sliderGender_female'),
                str(request.form.getlist('choice_education')).replace("'", ""),
                str(request.form.getlist('choice_occupation')).replace("'", ""),
                str(request.form.getlist('choice_life_stage')).replace("'", ""),
                request.form.get('b2c_location'),
                request.form.get('b2b_location'),
                request.form.get('preferences'),
                request.form.get('choices_industry'),
                request.form.get('segment_company_size'),
                show_age_range, show_income_range, show_gender_percentage, show_education, show_occupation,
                show_life_stage,
                bplan_id,
                request.form.get('mkt_segment_id')
            )

            segment_id = request.form.get('mkt_segment_id')

        if request.form.get('action') == "new_segment":
            optional_fields = "on" if request.form.get('show_age_range') == 'on' else "off"
            # Get all switch values from the form
            show_age_range = "on" if request.form.get('show_age_range') == 'on' else "off"
            show_income_range = "on" if request.form.get('show_income_range') == 'on' else "off"
            show_gender_percentage = "on" if request.form.get('show_gender_percentage') == 'on' else "off"
            show_education = "on" if request.form.get('show_education') == 'on' else "off"
            show_occupation = "on" if request.form.get('show_occupation') == 'on' else "off"
            show_life_stage = "on" if request.form.get('show_life_stage') == 'on' else "off"

            # Call the function with all switches
            update_buz_mkt_analysis(
                request.form.get('segment_name'),
                request.form.get('choice_business_model'),
                request.form.get('segment_percentage'),
                str(request.form.getlist('choice_marketing_channel')).replace("'", ""),
                request.form.get('sliderAge_min'), request.form.get('sliderAge_max'),
                request.form.get('sliderIncome_min'), request.form.get('sliderIncome_max'),
                request.form.get('sliderGender_male'), request.form.get('sliderGender_female'),
                str(request.form.getlist('choice_education')).replace("'", ""),
                str(request.form.getlist('choice_occupation')).replace("'", ""),
                str(request.form.getlist('choice_life_stage')).replace("'", ""),
                request.form.get('b2c_location'),
                request.form.get('b2b_location'),
                request.form.get('preferences'),
                request.form.get('choices_industry'),
                request.form.get('segment_company_size'),
                show_age_range, show_income_range, show_gender_percentage, show_education, show_occupation,
                show_life_stage,
                bplan_id,
                request.form.get('mkt_segment_id')
            )

            add_buz_mkt_segments(bplan_id)
            segment_id = get_last_mkt_segments(bplan_id)

        if request.form.get('select_segment') != None:
            segment_id = request.form.get('select_segment')

        if request.form.get('segment_delete') is not None:
            segment_to_delete = request.form.get("segment_delete")

            # Get how many segments this business plan currently has
            data_buz_mkt_segments, status_buz_mkt_segments = get_buz_mkt_segments(bplan_id)

            if len(data_buz_mkt_segments) <= 1:
                # Prevent deleting the last remaining segment
                flash("⚠️ You must have at least one segment for this business plan.", "warning")
                return redirect(url_for('home_blueprint.market_analysis', bplan_id=bplan_id))

            # Safe to delete
            buz_mkt_segments_delete(segment_to_delete)
            flash("Segment deleted successfully.", "success")
            return redirect(url_for('home_blueprint.market_analysis', bplan_id=bplan_id))


    else:
        segment_id = get_last_mkt_segments(bplan_id)

    data_completion, status_completion = get_completion(bplan_id)

    data_buz_mkt_segments, status_buz_mkt_segments = get_buz_mkt_segments(bplan_id) #buttons for all available segments 
    data_buz_mkt_analysis, status_buz_mkt_analysis = get_buz_mkt_analysis(bplan_id, segment_id) #display the selected segment details
    market_channel_list = ast.literal_eval(data_buz_mkt_analysis[0].get("market_channel"))
     
    
    data_price_preferences, status_price_preferences = get_preferences (bplan_id, '1', False)
    data_service_preferences, status_service_preferences = get_preferences (bplan_id, '2', False)
    data_quality_preferences, status_quality_preferences = get_preferences (bplan_id, '3', False)
    data_location_preferences, status_location_preferences = get_preferences (bplan_id, '4', False)
    # data_mkt_channels, status_mkt_channels = get_mkt_channels()
    
    education_list = ast.literal_eval(data_buz_mkt_analysis[0].get("education"))
    occupation_list = ast.literal_eval(data_buz_mkt_analysis[0].get("occupation"))
    life_stage_list = ast.literal_eval(data_buz_mkt_analysis[0].get("life_stage"))

    #old one location_list = ast.literal_eval(data_buz_mkt_analysis[0].get("location"))

    # Add this near the end before render_template
    data_b2b_clients = get_b2b_clients(segment_id)

    return render_template('home/marketanalysis.html',
                           segment='marketanalysis',
                           data_comp=data_completion,
                           data_mkt_segments=data_buz_mkt_segments,
                           data_price=data_price_preferences,
                           data_service=data_service_preferences,
                           data_quality=data_quality_preferences,
                           data_location=data_location_preferences,
                           data_mkt_analysis=data_buz_mkt_analysis,
                           market_channel_list=market_channel_list,
                           education_list=education_list,
                           occupation_list=occupation_list,
                           life_stage_list=life_stage_list,
                           data_b2b_clients=data_b2b_clients,  # ← ADD THIS
                           bplan_id=bplan_id,
                           segment_id=segment_id)


def reset_all_preferences_selection(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute("""
            UPDATE public.buz_preferences
            SET is_selected = FALSE
            WHERE bplan_id = %s;
        """, (bplan_id,))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error resetting selections:", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
def set_preference_selected(bplan_id, preference, selected=True):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute("""
            UPDATE public.buz_preferences
            SET is_selected = %s
            WHERE bplan_id = %s AND preference = %s;
        """, (selected, bplan_id, preference))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error setting preference:", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
def get_selected_preferences(bplan_id):
    conn = None
    selected = []
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute("""
            SELECT preference
            FROM public.buz_preferences
            WHERE bplan_id = %s AND is_selected = TRUE;
        """, (bplan_id,))
        rows = cur.fetchall()
        selected = [r[0] for r in rows]
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error getting selected preferences:", error)
    finally:
        if conn is not None:
            conn.close()
    return selected



# ==================== AI SEGMENT SUGGESTION HELPER ====================

def suggest_market_segments(client, business_description, lang='en'):
    """
    Use GPT to suggest market segments based on business description
    Returns a list of segment suggestions with name, business model, and description
    """

    if lang == 'ar':
        prompt = """أنت خبير في تحليل السوق. بناءً على وصف العمل التالي، اقترح 4-5 قطاعات سوقية مناسبة.

لكل قطاع، قدم:
1. اسم القطاع (قصير ومحدد)
2. نموذج العمل (B2B أو B2C)
3. وصف مختصر (جملة واحدة)
4. النسبة المئوية المقترحة من إجمالي السوق

أجب بصيغة JSON فقط، بدون أي نص إضافي:
{
    "segments": [
        {
            "name": "اسم القطاع",
            "business_model": "B2B",
            "description": "وصف مختصر",
            "suggested_percentage": 25
        }
    ]
}

وصف العمل:"""
    else:
        prompt = """You are a market analysis expert. Based on the following business description, suggest 4-5 appropriate market segments.

For each segment, provide:
1. Segment name (short and specific)
2. Business model (B2B or B2C)
3. Brief description (one sentence)
4. Suggested percentage of total market

Respond ONLY with valid JSON, no additional text:
{
    "segments": [
        {
            "name": "Segment Name",
            "business_model": "B2B",
            "description": "Brief description",
            "suggested_percentage": 25
        }
    ]
}

Business description:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are a market segmentation expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt + "\n\n" + business_description}
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        # Clean up the response - remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        import json
        result = json.loads(content)
        return result.get("segments", [])

    except Exception as e:
        print(f"Error in suggest_market_segments: {e}")
        return []


# ==================== ROUTE: Get AI Suggestions ====================

@blueprint.route('/api/suggest_segments/<bplan_id>', methods=['POST'])
@login_required
def api_suggest_segments(bplan_id):
    """
    AJAX endpoint to get AI-suggested market segments
    """
    from openai import OpenAI

    try:
        data = request.get_json()
        business_description = data.get('description', '').strip()

        if not business_description:
            return jsonify({
                'success': False,
                'error': 'Please provide a business description'
            }), 400

        if len(business_description) < 10:
            return jsonify({
                'success': False,
                'error': 'Please provide a more detailed description'
            }), 400

        # Get language from session
        lang = session.get('lang', 'en')

        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Get suggestions
        segments = suggest_market_segments(client, business_description, lang)

        if not segments:
            return jsonify({
                'success': False,
                'error': 'Could not generate suggestions. Please try again.'
            }), 500

        return jsonify({
            'success': True,
            'segments': segments
        })

    except Exception as e:
        print(f"Error in api_suggest_segments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ROUTE: Get AI Suggestions with Context ====================

@blueprint.route('/api/suggest_segments_smart/<bplan_id>', methods=['POST'])
@login_required
def api_suggest_segments_smart(bplan_id):
    """
    AJAX endpoint to get AI-suggested market segments
    Uses existing business plan data for context
    """
    from openai import OpenAI

    try:
        data = request.get_json()
        user_description = data.get('description', '').strip()

        # Get existing business info for context
        data_buz_info, _ = get_buz_info(bplan_id)
        data_bplan, _ = get_bplan(bplan_id)

        # Build context from existing data
        context_parts = []

        if data_bplan and len(data_bplan) > 0:
            if data_bplan[0].get('name'):
                context_parts.append(f"Business name: {data_bplan[0]['name']}")
            if data_bplan[0].get('industry'):
                context_parts.append(f"Industry: {data_bplan[0]['industry']}")
            if data_bplan[0].get('buz_sector'):
                context_parts.append(f"Sector: {data_bplan[0]['buz_sector']}")

        if data_buz_info and len(data_buz_info) > 0:
            if data_buz_info[0].get('product_services'):
                context_parts.append(f"Products/Services: {data_buz_info[0]['product_services']}")

        # Combine context with user description
        full_description = user_description
        if context_parts:
            full_description = "\n".join(context_parts) + "\n\nAdditional details: " + user_description

        if len(full_description) < 10:
            return jsonify({
                'success': False,
                'error': 'Please provide a business description'
            }), 400

        # Get language from session
        lang = session.get('lang', 'en')

        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Get suggestions
        segments = suggest_market_segments(client, full_description, lang)

        if not segments:
            return jsonify({
                'success': False,
                'error': 'Could not generate suggestions. Please try again.'
            }), 500

        return jsonify({
            'success': True,
            'segments': segments
        })

    except Exception as e:
        print(f"Error in api_suggest_segments_smart: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ROUTE: Add Segment to Database ====================

@blueprint.route('/api/add_segment/<bplan_id>', methods=['POST'])
@login_required
def api_add_segment(bplan_id):
    """
    AJAX endpoint to add a new segment to the database
    Creates segment with name, business model, and suggested percentage
    """
    try:
        data = request.get_json()
        segment_name = data.get('name', '').strip()
        business_model = data.get('business_model', 'B2C').strip()
        suggested_percentage = data.get('suggested_percentage', 0)

        if not segment_name:
            return jsonify({
                'success': False,
                'error': 'Segment name is required'
            }), 400

        # Validate business model
        if business_model not in ['B2B', 'B2C']:
            business_model = 'B2C'

        # Validate percentage
        try:
            suggested_percentage = float(suggested_percentage)
            if suggested_percentage < 0 or suggested_percentage > 100:
                suggested_percentage = 0
        except:
            suggested_percentage = 0

        # Step 1: Create a new segment (this creates with default values)
        add_buz_mkt_segments(bplan_id)

        # Step 2: Get the ID of the newly created segment
        new_segment_id = get_last_mkt_segments(bplan_id)

        if not new_segment_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create segment'
            }), 500

        # Step 3: Update the segment with the AI-suggested values
        # Using default values for all other fields
        update_buz_mkt_analysis(
            segment_name=segment_name,
            business_model=business_model,
            segment_percentage=suggested_percentage,
            market_channel='[]',  # Empty array
            age_min=20,
            age_max=80,
            income_min=500,
            income_max=8000,
            male_rate=49,
            female_rate=51,
            education='[]',
            occupation='[]',
            life_stage='[]',
            b2c_location='',
            b2b_location='',
            preferences='',
            industry='',
            company_size='',
            show_age_range='off',
            show_income_range='off',
            show_gender_percentage='off',
            show_education='off',
            show_occupation='off',
            show_life_stage='off',
            bplan_id=bplan_id,
            segment_id=new_segment_id
        )

        return jsonify({
            'success': True,
            'segment_id': new_segment_id,
            'message': 'Segment added successfully'
        })

    except Exception as e:
        print(f"Error in api_add_segment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500





@blueprint.route('/competitors/<bplan_id>', methods=['GET', 'POST'])
@login_required
def competitors(bplan_id):
    import ast

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_preferences':
            print('update preferences request')

            # Get the 3 chosen preferences from form
            selected_prefs = [
                request.form.get('preference_1'),
                request.form.get('preference_2'),
                request.form.get('preference_3')
            ]

            # Validate at least one preference is selected
            selected_prefs = [pref for pref in selected_prefs if pref]
            if not selected_prefs:
                return jsonify({
                    'success': False,
                    'message': 'Please select at least one preference'
                }), 400

            # Reset all selections to False first
            reset_all_preferences_selection(bplan_id)

            # Mark the selected preferences as selected=True
            for pref in selected_prefs:
                set_preference_selected(bplan_id, pref, True)

            return jsonify({
                'success': True,
                'message': f'Successfully updated {len(selected_prefs)} preferences',
                'selected_preferences': selected_prefs
            })

        elif action == 'save':
            print('save request competitors')
            update_bplan_completion('complete_competitors', bplan_id)

            # Step 1: Get all available preferences
            data_competitors_preferences, _ = get_preferences(bplan_id, '', True)

            # Step 2: Reset all selections to False first
            reset_all_preferences_selection(bplan_id)

            # Step 3: Get the 3 chosen preferences from form
            selected_prefs = [
                request.form.get('preference_1'),
                request.form.get('preference_2'),
                request.form.get('preference_3')
            ]

            # Step 4: Mark these 3 as selected=True
            for pref in selected_prefs:
                if pref:
                    set_preference_selected(bplan_id, pref, True)

            # Step 5: Update competitor names and values
            update_buz_competitor(
                request.form.get('first_competitor_name'),
                request.form.get('second_competitor_name'),
                request.form.get('third_competitor_name'),
                bplan_id
            )

            for data in data_competitors_preferences:
                update_competitors_preferences(
                    bplan_id,
                    data['preference'],
                    request.form.get(data['preference'] + "_1"),
                    request.form.get(data['preference'] + "_2"),
                    request.form.get(data['preference'] + "_3")
                )

            return redirect(url_for('home_blueprint.operations_plan', bplan_id=bplan_id))

    # Step 6: Retrieve data for GET
    data_completion, _ = get_completion(bplan_id)
    data_buz_mkt_segments, _ = get_buz_mkt_segments(bplan_id)
    data_buz_competitor, _ = get_buz_competitor(bplan_id)
    data_competitors_preferences, _ = get_preferences(bplan_id, '', True)

    # Step 7: Get selected preferences to pre-fill dropdowns
    selected_preferences = get_selected_preferences(bplan_id)

    return render_template(
        'home/competitors.html',
        segment='competitors',
        data_comp=data_completion,
        data_mkt_segments=data_buz_mkt_segments,
        data_compname=data_buz_competitor,
        data_competitors=data_competitors_preferences,
        selected_preferences=selected_preferences,
        bplan_id=bplan_id
    )

@blueprint.route('/operations_plan/<bplan_id>', methods=['GET', 'POST'])
@login_required
def operations_plan(bplan_id):
    if request.method == 'POST':
        # Handle Supplier Addition
        if request.form.get('supplier_add') is not None:
            supplier_id, error = supplier_add(
                bplan_id=bplan_id,
                supplier_name=request.form['supplier_name'],
                years_of_collaboration=request.form['choice_collaboration'],
                performance_type=request.form.get('choice_performance_type', 'N/A'),
                quality=request.form['choice_quality'],
                customer_service=request.form['choice_customer_service']
            )
            if error:
                flash(f'Error adding supplier: {error}', 'error')
            else:
                flash('Supplier added successfully', 'success')

        # Handle Product Addition (separate form)
        elif request.form.get('product_add') is not None:
            product_id, error = supplier_product_add(
                supplier_id=request.form['supplier_id'],
                bplan_id=bplan_id,
                product_service=request.form['product_service'],
                prices=request.form['choice_prices'],
                quantity=request.form['choice_quantity']
            )
            if error:
                flash(f'Error adding product: {error}', 'error')
            else:
                flash('Product added successfully', 'success')

        # Handle Product Deletion
        elif request.form.get('supplier_product_delete') is not None:
            print("Delete request received:", request.form['supplier_product_delete'])  # Debug
            ids = request.form['supplier_product_delete'].split('_')
            print("Split IDs:", ids)  # Debug
            if len(ids) == 2:
                print(f"Attempting to delete product {ids[1]} from supplier {ids[0]}")  # Debug
                success, message = supplier_product_delete(ids[0], ids[1])
                print("Delete result:", success, message)  # Debug

        # Handle Supplier Deletion
        elif request.form.get('supplier_delete') is not None:
            success, message = supplier_delete(request.form['supplier_delete'])
            if not success:
                flash(f'Error deleting supplier: {message}', 'error')
            else:
                flash(message, 'success')

        # Production handlers
        elif request.form.get('production_add') is not None:
            production_add(
                request.form['production_add'], '',
                request.form['choice_production_unit'],
                request.form['choice_time_frame'],
                request.form['current_capacity'],
                request.form['max_expected_capacity']
            )

        elif request.form.get('production_delete') is not None:
            production_delete(request.form['production_delete'])

        # Distribution handlers - FIXED VERSION
        elif request.form.get('distribution_add') is not None:
            print("DEBUG: distribution Add button clicked")  # <-- this will show in your console
            print("Form data received:", request.form)

            # FIX: Use get() instead of direct access to handle missing fields
            distributor_name = request.form.get('distributor_name', '')
            distribution_type = request.form['choice_type']
            collaboration_years = request.form['dis_collaboration_years']

            # For Online and Direct Sales, use the type as name if no distributor name provided
            if distribution_type in ['Online', 'Direct Sales'] and not distributor_name:
                distributor_name = distribution_type

            distribution_add(
                request.form['distribution_add'],
                distributor_name,
                distribution_type,
                collaboration_years
            )

        elif request.form.get('distribution_delete') is not None:
            distribution_delete(request.form['distribution_delete'])

        elif request.form.get('action') == 'save':
            update_bplan_completion('complete_operations_plan', bplan_id)

            update_buz_operation_plan(
                str(request.form.getlist('choice_enhance')).replace("'", ""),
                str(request.form.getlist('choice_customer_support')).replace("'", ""),
                bplan_id
            )
            return redirect(url_for('home_blueprint.requested_fund', bplan_id=bplan_id))

        # ✅ ADD THIS AJAX DETECTION RIGHT BEFORE THE REDIRECT:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return full page for AJAX requests
            data_completion, status_completion = get_completion(bplan_id)
            data_buz_supplier, status_buz_supplier = get_buz_supplier(bplan_id)

            # Get products for all suppliers
            if data_buz_supplier is not None:
                for supplier in data_buz_supplier:
                    products, _ = get_products_buz_supplier(supplier['supplier_id'])
                    supplier['products'] = products if products is not None else []
            else:
                data_buz_supplier = []

            data_buz_production, status_buz_production = get_buz_production(bplan_id)
            data_buz_distribution, status_buz_distribution = get_buz_distribution(bplan_id)
            data_buz_operation_plan, status_buz_operation_plan = get_buz_operation_plan(bplan_id)

            return render_template('home/operationsplan.html',
                                   segment='operationsplan',
                                   data_comp=data_completion,
                                   data_bs=data_buz_supplier,
                                   data_bp=data_buz_production,
                                   data_bd=data_buz_distribution,
                                   data_op=data_buz_operation_plan,
                                   bplan_id=bplan_id)

        return redirect(url_for('home_blueprint.operations_plan', bplan_id=bplan_id))

    # GET Request Handling
    data_completion, status_completion = get_completion(bplan_id)
    data_buz_supplier, status_buz_supplier = get_buz_supplier(bplan_id)

    # Get products for all suppliers (if needed for display)
    if data_buz_supplier is not None:
        for supplier in data_buz_supplier:
            products, _ = get_products_buz_supplier(supplier['supplier_id'])
            supplier['products'] = products if products is not None else []
    else:
        data_buz_supplier = []

    data_buz_production, status_buz_production = get_buz_production(bplan_id)
    data_buz_distribution, status_buz_distribution = get_buz_distribution(bplan_id)
    data_buz_operation_plan, status_buz_operation_plan = get_buz_operation_plan(bplan_id)

    return render_template('home/operationsplan.html',
                           segment='operationsplan',
                           data_comp=data_completion,
                           data_bs=data_buz_supplier,
                           data_bp=data_buz_production,
                           data_bd=data_buz_distribution,
                           data_op=data_buz_operation_plan,
                           bplan_id=bplan_id)

@blueprint.route('/requested_fund/<bplan_id>', methods=['GET', 'POST'])
@login_required
def requested_fund(bplan_id):

    if request.method == 'POST':
        if request.form.get('buz_item_add') != None:
            print('in buzz add')
            buz_item_add(   request.form.get('buz_item_add'),
                                request.form.get('choice_item_type'),
                                request.form.get('item_name'),
                                request.form.get('choice_item_unit'),
                                request.form.get('item_quantity'),
                                request.form.get('item_cost'))
            update_buz_fund_details(    str(request.form.getlist('choice_objectives')).replace("'", ""),
                                        str(request.form.getlist('choice_purposes')).replace("'", ""),
                                        request.form.get('choice_fund_type'),
                                        request.form.get('fund_amount'),
                                        request.form.get('fund_equity'),
                                        request.form.get('interest_rate'),
                                        request.form.get('fund_period'),
                                        request.form.get('fund_grace_period'),
                                        bplan_id)

        if request.form.get('buz_item_delete') != None:
            buz_item_delete(request.form.get('buz_item_delete'))
            update_buz_fund_details(    str(request.form.getlist('choice_objectives')).replace("'", ""),
                                        str(request.form.getlist('choice_purposes')).replace("'", ""),
                                        request.form.get('choice_fund_type'),
                                        request.form.get('fund_amount'),
                                        request.form.get('fund_equity'),
                                        request.form.get('interest_rate'),
                                        request.form.get('fund_period'),
                                        request.form.get('fund_grace_period'),
                                        bplan_id)

            # ✅ ADD THIS AJAX DETECTION RIGHT BEFORE THE REDIRECT:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return full page for AJAX requests
                data_completion, status_completion = get_completion(bplan_id)
                status_fund_installation, data_fund_installation, data_fund_total = get_buz_fund_items(bplan_id, "1")
                status_fund_machines, data_fund_machines, data_fund_total = get_buz_fund_items(bplan_id, "2")
                status_fund_materials, data_fund_materials, data_fund_total = get_buz_fund_items(bplan_id, "3")
                status_fund_salaries, data_fund_salaries, data_fund_total = get_buz_fund_items(bplan_id, "4")
                status_fund_ocosts, data_fund_ocosts, data_fund_total = get_buz_fund_items(bplan_id, "5")
                data_fund_items, status_fund_items = get_buz_fund_details(bplan_id)

                return render_template('home/requestfund.html', segment='requestfund',
                                       data_comp=data_completion,
                                       data_installation=data_fund_installation,
                                       data_machines=data_fund_machines,
                                       data_materials=data_fund_materials,
                                       data_salaries=data_fund_salaries,
                                       data_ocosts=data_fund_ocosts,
                                       data_fund_total=data_fund_total,
                                       data_fd=data_fund_items,
                                       bplan_id=bplan_id)

        if request.form.get('action') == 'save':
            update_bplan_completion ('complete_requested_fund',bplan_id)
            update_buz_fund_details(    str(request.form.getlist('choice_objectives')).replace("'", ""),
                                        str(request.form.getlist('choice_purposes')).replace("'", ""),
                                        request.form.get('choice_fund_type'),
                                        request.form.get('fund_amount'),
                                        request.form.get('fund_equity'),
                                        request.form.get('interest_rate'),
                                        request.form.get('fund_period'),
                                        request.form.get('fund_grace_period'),
                                        bplan_id)

            return redirect(url_for('home_blueprint.feasibility', bplan_id=bplan_id))
        return redirect(url_for('home_blueprint.requested_fund', bplan_id=bplan_id))

    data_completion, status_completion = get_completion(bplan_id)
    status_fund_installation, data_fund_installation, data_fund_total = get_buz_fund_items (bplan_id, "1")
    status_fund_machines, data_fund_machines, data_fund_total = get_buz_fund_items (bplan_id, "2")
    status_fund_materials, data_fund_materials, data_fund_total = get_buz_fund_items (bplan_id, "3")
    status_fund_salaries, data_fund_salaries, data_fund_total = get_buz_fund_items (bplan_id, "4")
    status_fund_ocosts, data_fund_ocosts, data_fund_total = get_buz_fund_items (bplan_id, "5")
    data_fund_items, status_fund_items = get_buz_fund_details (bplan_id)

    return render_template('home/requestfund.html', segment='requestfund',
                           data_comp = data_completion,
                           data_installation = data_fund_installation,
                           data_machines = data_fund_machines,
                           data_materials = data_fund_materials,
                           data_salaries = data_fund_salaries,
                           data_ocosts = data_fund_ocosts,
                           data_fund_total = data_fund_total,
                           data_fd = data_fund_items,
                           bplan_id = bplan_id)

@blueprint.route('/feasibility/<bplan_id>', methods=['GET', 'POST'])
@login_required
def feasibility(bplan_id):
    DEFAULT_INFLATION_RATE = 3.0

    if request.method == 'POST':
        action = request.form.get('action')
        inflation_rate = float(request.form.get('assumptions_inflation_rate', DEFAULT_INFLATION_RATE))

        if action == 'update_inflation':
            # Update only inflation rate
            update_buz_inflation_rate(inflation_rate, bplan_id)
            return redirect(url_for('home_blueprint.feasibility', bplan_id=bplan_id))

        elif 'product_add' in request.form:
            _handle_product_add(bplan_id, request.form)

        elif 'product_delete' in request.form:
            product_delete(request.form.get('product_delete'))

        elif 'expense_add' in request.form:
            _handle_expense_add(bplan_id, request.form)

        elif 'expense_delete' in request.form:
            feasibilty_expense_delete(request.form.get('expense_delete'))

        elif action == 'save':
            return _handle_save_action(bplan_id, request.form)

        # Default redirect after handling any POST action

        # ✅ FIXED: Check for AJAX request AFTER handling the specific actions
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return _handle_feasibility_view(bplan_id)
        else:
            return redirect(url_for('home_blueprint.feasibility', bplan_id=bplan_id))
        # return redirect(url_for('home_blueprint.feasibility', bplan_id=bplan_id))

    # Handle GET requests
    return _handle_feasibility_view(bplan_id)
# Updated helper functions
def _handle_save_action(bplan_id, form_data):
    update_bplan_completion('complete_feasibility', bplan_id)

    # Update feasibility data (without inflation rate)
    update_buz_feasibility(
        form_data.get('first_year'),
        form_data.get('second_year'),
        form_data.get('third_year'),
        form_data.get('fourth_year'),
        form_data.get('fifth_year'),
        form_data.get('assumptions_annual_growth'),
        form_data.get('assumptions_depreciation'),
        bplan_id
    )

    # Update resource depreciation
    _, data_buz_resource, _ = get_buz_resource(bplan_id)
    for data in data_buz_resource:
        update_buz_resource(
            data['resource_id'],
            form_data.get(f'depreciation_{data["resource_id"]}')
        )

    return redirect(url_for('home_blueprint.export_plan', bplan_id=bplan_id))
def _handle_feasibility_view(bplan_id):
    # Fetch all required data
    data_completion, _ = get_completion(bplan_id)
    data_buz_product = get_buz_product(bplan_id)[0] or []
    data_buz_expenses = get_buz_expenses(bplan_id)[0] or []
    data_buz_feasibility = get_buz_feasibility(bplan_id)[0] or []
    _, data_buz_resource, data_buz_total_resources = get_buz_resource(bplan_id)

    # Get inflation rate from dedicated function
    inflation_data, _ = get_buz_inflation_rate(bplan_id)
    inflation_rate = float(inflation_data[0]['inflation_rate']) if inflation_data else 3.0

    # Calculate projections
    data_projections, data_total_projections = calculate_projections(
        data_buz_product,
        data_buz_expenses,
        inflation_rate=inflation_rate
    )

    return render_template(
        'home/feasibility.html',
        segment='feasibility',
        data_comp=data_completion,
        data_bp=data_buz_product,
        data_expenses=data_buz_expenses,
        data_com=data_buz_feasibility,
        data_br=data_buz_resource,
        data_projections=data_projections,
        data_total_projections=data_total_projections,
        bplan_id=bplan_id,
        current_inflation_rate=inflation_rate
    )
def _handle_product_add(bplan_id, form_data):
    # Helper function to convert multi-select values to pipe-separated string
    def get_multiselect_reasons(year):
        reasons = form_data.getlist(f'growth_reason_year{year}')
        return '|'.join(reasons) if reasons else None

    product_add(
        bplan_id,
        form_data.get('product_service_id'),
        form_data.get('unit'),
        form_data.get('price'),
        form_data.get('cost'),
        form_data.get('growth_prct_year1'),
        form_data.get('growth_prct_year2'),
        form_data.get('growth_prct_year3'),
        form_data.get('growth_prct_year4'),
        form_data.get('growth_prct_year5'),
        get_multiselect_reasons(1),
        get_multiselect_reasons(2),
        get_multiselect_reasons(3),
        get_multiselect_reasons(4),
        get_multiselect_reasons(5)
    )

def _handle_expense_add(bplan_id, form_data):
    expense_add(
        bplan_id,
        form_data.get('expense_type'),
        form_data.get('unit_quantity'),
        form_data.get('price')
    )




@blueprint.route('/profit_loss', methods=['GET', 'POST'])
@login_required
def profit_loss():

    if request.form.get('option') == 'previous':
        return render_template('home/requestfund.html', segment='requestfund')
    elif request.form.get('option') == 'save':
        return render_template('home/profitloss.html', segment='profitloss')

@blueprint.route('/breakeven', methods=['GET', 'POST'])
@login_required
def breakeven(bplan_id):

    if request.form.get('option') == 'previous':
        return render_template('home/feasibility.html', segment='feasibility')
    elif request.form.get('option') == 'save':
        return render_template('home/breakeven.html', segment='breakeven')


############################################################################################################################################################################
from flask import send_file
import io
import base64
from threading import Thread
import time


# import pdfkit
from flask import make_response, render_template
# from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ============================================================
# STEP 1: ADD THIS PROGRESS TRACKING CODE AT THE TOP OF routes.py
# (After your imports)
# ============================================================

import threading
from datetime import datetime
from flask import jsonify

# Thread-safe progress storage
_progress_store = {}
_progress_lock = threading.Lock()


def init_progress(bplan_id, sections):
    """Initialize progress tracking for a business plan generation."""
    with _progress_lock:
        _progress_store[bplan_id] = {
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'current_phase': 'initializing',
            'sections': {
                section: {
                    'status': 'pending',
                    'started_at': None,
                    'completed_at': None,
                    'message': ''
                } for section in sections
            },
            'total_sections': len(sections),
            'completed_sections': 0,
            'mission_vision': {'status': 'pending', 'message': ''},
            'objectives': {'status': 'pending', 'message': ''}
        }
    return True


def update_section_progress(bplan_id, section_key, status, message=''):
    """Update progress for a specific section."""
    with _progress_lock:
        if bplan_id not in _progress_store:
            return False

        progress = _progress_store[bplan_id]

        if section_key in ['mission_vision', 'objectives']:
            progress[section_key]['status'] = status
            progress[section_key]['message'] = message
        elif section_key in progress['sections']:
            section = progress['sections'][section_key]

            if status == 'in_progress' and section['started_at'] is None:
                section['started_at'] = datetime.now().isoformat()

            section['status'] = status
            section['message'] = message

            if status == 'completed':
                section['completed_at'] = datetime.now().isoformat()
                progress['completed_sections'] = sum(
                    1 for s in progress['sections'].values() if s['status'] == 'completed'
                )

        # Update current phase
        in_progress = [k for k, v in progress['sections'].items() if v['status'] == 'in_progress']
        if in_progress:
            progress['current_phase'] = in_progress[0]

    return True


def get_progress(bplan_id):
    """Get current progress for a business plan."""
    with _progress_lock:
        if bplan_id in _progress_store:
            return dict(_progress_store[bplan_id])
    return None


def mark_generation_complete(bplan_id):
    """Mark the entire generation process as complete."""
    with _progress_lock:
        if bplan_id in _progress_store:
            _progress_store[bplan_id]['status'] = 'completed'
            _progress_store[bplan_id]['completed_at'] = datetime.now().isoformat()
    return True


def clear_progress(bplan_id):
    """Clear progress tracking for a business plan."""
    with _progress_lock:
        if bplan_id in _progress_store:
            del _progress_store[bplan_id]
    return True


# ============================================================
# STEP 2: REPLACE YOUR EXISTING export_plan ROUTE WITH THIS
# ============================================================

@blueprint.route('/export_plan/<bplan_id>', methods=['GET', 'POST'])
@login_required
def export_plan(bplan_id):
    import json
    import os
    import re
    import threading
    import time

    # Fetch your data (moved before POST so it can be reused for rendering and PDF)
    lang = session.get('lang', 'en')
    data_get_bplan, status_get_bplan = get_bplan(bplan_id)
    print(data_get_bplan[0]['name'])
    data_export_plan, status_export_plan = get_export_plan(bplan_id)
    data_buz_financial, status_buz_financial = get_buz_financial(bplan_id)
    status_buz_staff, data_buz_staff, data_buz_total_salaries = get_buz_staff(bplan_id)
    data_buz_premises_photo, status_buz_premises_photo = get_buz_premises_photo(bplan_id)
    data_competitors_preferences, status_competitors_preferences = get_preferences(bplan_id, '', True)
    status_expenses, data_expenses, total_expenses = get_expenses(bplan_id)
    status_buz_resource, data_buz_resource, data_buz_total_resources = get_buz_resource(bplan_id)
    status_fund_installation, data_fund_installation, data_fund_total = get_buz_fund_items(bplan_id, "1")
    status_fund_machines, data_fund_machines, data_fund_total = get_buz_fund_items(bplan_id, "2")
    status_fund_materials, data_fund_materials, data_fund_total = get_buz_fund_items(bplan_id, "3")
    status_fund_salaries, data_fund_salaries, data_fund_total = get_buz_fund_items(bplan_id, "4")
    status_fund_ocosts, data_fund_ocosts, data_fund_total = get_buz_fund_items(bplan_id, "5")
    data_buz_mkt_segments, status_buz_mkt_segments = get_buz_mkt_segments(bplan_id)

    # Operations data for charts
    data_buz_suppliers, _ = get_buz_supplier(bplan_id)
    data_buz_production, _ = get_buz_production(bplan_id)
    data_buz_distribution, _ = get_buz_distribution(bplan_id)

    # Client Profile additional data for charts
    data_partners, _ = get_partners(bplan_id)
    data_experiences, _ = get_experiences(bplan_id)

    # Attach products to each supplier
    for supplier in data_buz_suppliers:
        products, _ = get_products_buz_supplier(supplier['supplier_id'])
        supplier['products'] = products if products else []

    data_export_plan_checkboxes, status_export_plan_checkboxes = get_buz_export_plan_checkboxes(bplan_id)

    # NEW: Fetch feasibility data for the projections table
    data_buz_product = get_buz_product(bplan_id)[0] or []
    data_buz_expenses = get_buz_expenses(bplan_id)[0] or []

    # Get inflation rate from dedicated function
    inflation_data, _ = get_buz_inflation_rate(bplan_id)
    inflation_rate = float(inflation_data[0]['inflation_rate']) if inflation_data else 3.0

    # Calculate projections (same as in feasibility page)
    data_projections, data_total_projections = calculate_projections(
        data_buz_product,
        data_buz_expenses,
        inflation_rate=inflation_rate
    )
    data_price_preferences, status_price_preferences = get_preferences(bplan_id, '1', False)
    data_service_preferences, status_service_preferences = get_preferences(bplan_id, '2', False)
    data_quality_preferences, status_quality_preferences = get_preferences(bplan_id, '3', False)
    data_location_preferences, status_location_preferences = get_preferences(bplan_id, '4', False)
    data_comp_preferences, status_comp_preferences = get_selected_preferences_only(bplan_id)
    data_buz_competitor, _ = get_buz_competitor(bplan_id)

    # POST request handling
    if request.method == 'POST':

        # ---------------------- SCREENSHOT PDF OPTION ----------------------
        if request.form.get('action') == 'screenshot_pdf':
            try:
                import tempfile
                from PIL import Image
                import img2pdf

                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.set_viewport_size({"width": 1200, "height": 800})
                    screenshot_url = f"http://localhost:5000/export_plan/{bplan_id}?screenshot=true"
                    page.goto(screenshot_url)
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)

                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        screenshot_path = tmp.name

                    page.screenshot(path=screenshot_path, full_page=True)
                    browser.close()

                    image = Image.open(screenshot_path)
                    pdf_bytes = img2pdf.convert(image.filename)
                    os.remove(screenshot_path)

                    response = make_response(pdf_bytes)
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Disposition'] = f'attachment; filename=export_plan_{bplan_id}.pdf'
                    return response

            except Exception as e:
                print(f"Playwright screenshot error: {e}")
                return f"Error generating screenshot: {e}", 500

        # ---------------------- GENERATE OPTION (WITH PROGRESS TRACKING) ----------------------
        if request.form.get('action') == 'generate':
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)
            query_model = "gpt-4o-mini"

            # Determine which sections are being generated
            sections_to_generate = []
            if request.form.get('flexSwitchCheck_client_profile'):
                sections_to_generate.append('client_profile')
            if request.form.get('flexSwitchCheck_business_profile'):
                sections_to_generate.append('business_profile')
            if request.form.get('flexSwitchCheck_business_premises'):
                sections_to_generate.append('business_premises')
            if request.form.get('flexSwitchCheck_market_analysis'):
                sections_to_generate.append('market_analysis')
            if request.form.get('flexSwitchCheck_operations_plan'):
                sections_to_generate.append('operations_plan')
            if request.form.get('flexSwitchCheck_requested_fund'):
                sections_to_generate.append('requested_fund')
            if request.form.get('flexSwitchCheck_feasibility'):
                sections_to_generate.append('feasibility')

            # Initialize progress tracking
            init_progress(bplan_id, sections_to_generate)

            time.sleep(1)
            all_threads = []

            # ==================== CLIENT PROFILE ====================
            if request.form.get('flexSwitchCheck_client_profile') is not None:
                update_section_progress(bplan_id, 'client_profile', 'in_progress', 'Starting client profile...')

                def tracked_client_info():
                    try:
                        get_api_content_client_info(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in client_info: {e}")

                def tracked_client_experience():
                    try:
                        get_api_content_client_experience(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in client_experience: {e}")

                def tracked_client_partners():
                    try:
                        get_api_content_client_partners(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in client_partners: {e}")

                def tracked_client_expenses():
                    try:
                        get_api_content_client_expenses(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in client_expenses: {e}")

                def tracked_client_employed():
                    try:
                        get_api_content_client_employed(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in client_employed: {e}")

                def tracked_client_side_business():
                    try:
                        get_api_content_client_side_business(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in client_side_business: {e}")

                threads = [
                    threading.Thread(target=tracked_client_info),
                    threading.Thread(target=tracked_client_experience),
                    threading.Thread(target=tracked_client_partners),
                    threading.Thread(target=tracked_client_expenses),
                    threading.Thread(target=tracked_client_employed),
                    threading.Thread(target=tracked_client_side_business)
                ]
                for thread in threads:
                    thread.start()
                all_threads.extend(threads)

            # ==================== BUSINESS PROFILE ====================
            if request.form.get('flexSwitchCheck_business_profile') is not None:
                update_section_progress(bplan_id, 'business_profile', 'in_progress', 'Starting business profile...')

                def tracked_business_profile():
                    try:
                        get_api_content_business_profile(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in business_profile: {e}")

                def tracked_buz_product_services():
                    try:
                        get_api_content_buz_product_services(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in buz_product_services: {e}")

                def tracked_buz_staff():
                    try:
                        get_api_content_buz_staff(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in buz_staff: {e}")

                def tracked_buz_resources():
                    try:
                        get_api_content_buz_resources(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in buz_resources: {e}")

                def tracked_source_funding():
                    try:
                        get_api_content_source_funding(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in source_funding: {e}")

                def tracked_financial_history():
                    try:
                        get_api_content_financial_history(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in financial_history: {e}")

                threads = [
                    threading.Thread(target=tracked_business_profile),
                    threading.Thread(target=tracked_buz_product_services),
                    threading.Thread(target=tracked_buz_staff),
                    threading.Thread(target=tracked_buz_resources),
                    threading.Thread(target=tracked_source_funding),
                    threading.Thread(target=tracked_financial_history)
                ]
                for thread in threads:
                    thread.start()
                all_threads.extend(threads)

            # ==================== BUSINESS PREMISES ====================
            if request.form.get('flexSwitchCheck_business_premises') is not None:
                update_section_progress(bplan_id, 'business_premises', 'in_progress',
                                        'Generating premises description...')

                def tracked_business_premises():
                    try:
                        get_api_content_business_premises(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in business_premises: {e}")

                thread = threading.Thread(target=tracked_business_premises)
                thread.start()
                all_threads.append(thread)

            # ==================== MARKET ANALYSIS ====================
            if request.form.get('flexSwitchCheck_market_analysis') is not None:
                update_section_progress(bplan_id, 'market_analysis', 'in_progress', 'Analyzing market data...')

                def tracked_market_analysis():
                    try:
                        get_api_content_market_analysis(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in market_analysis: {e}")

                thread = threading.Thread(target=tracked_market_analysis)
                thread.start()
                all_threads.append(thread)

            # ==================== OPERATIONS PLAN ====================
            if request.form.get('flexSwitchCheck_operations_plan') is not None:
                update_section_progress(bplan_id, 'operations_plan', 'in_progress', 'Planning operations...')

                def tracked_buz_suppliers():
                    try:
                        get_api_content_buz_suppliers(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in buz_suppliers: {e}")

                def tracked_buz_production():
                    try:
                        get_api_content_buz_production(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in buz_production: {e}")

                def tracked_buz_distribution():
                    try:
                        get_api_content_buz_distribution(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in buz_distribution: {e}")

                threads = [
                    threading.Thread(target=tracked_buz_suppliers),
                    threading.Thread(target=tracked_buz_production),
                    threading.Thread(target=tracked_buz_distribution)
                ]
                for thread in threads:
                    thread.start()
                all_threads.extend(threads)

            # ==================== REQUESTED FUND ====================
            if request.form.get('flexSwitchCheck_requested_fund') is not None:
                update_section_progress(bplan_id, 'requested_fund', 'in_progress',
                                        'Calculating funding requirements...')

                def tracked_requested_fund():
                    try:
                        get_api_content_requested_fund(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in requested_fund: {e}")

                thread = threading.Thread(target=tracked_requested_fund)
                thread.start()
                all_threads.append(thread)

            # ==================== FEASIBILITY ====================
            if request.form.get('flexSwitchCheck_feasibility') is not None:
                update_section_progress(bplan_id, 'feasibility', 'in_progress', 'Analyzing feasibility...')

                def tracked_feasibility():
                    try:
                        get_api_content_feasibility(client, query_model, bplan_id, lang)
                    except Exception as e:
                        print(f"Error in feasibility: {e}")

                thread = threading.Thread(target=tracked_feasibility)
                thread.start()
                all_threads.append(thread)

            # ==================== WAIT FOR ALL THREADS ====================
            print(f"DEBUG: Waiting for {len(all_threads)} threads to complete...")
            for thread in all_threads:
                thread.join(timeout=60)
            print("DEBUG: All content generation threads completed")

            # Mark sections as completed
            if request.form.get('flexSwitchCheck_client_profile'):
                update_section_progress(bplan_id, 'client_profile', 'completed', 'Client profile completed')
            if request.form.get('flexSwitchCheck_business_profile'):
                update_section_progress(bplan_id, 'business_profile', 'completed', 'Business profile completed')
            if request.form.get('flexSwitchCheck_business_premises'):
                update_section_progress(bplan_id, 'business_premises', 'completed', 'Business premises completed')
            if request.form.get('flexSwitchCheck_market_analysis'):
                update_section_progress(bplan_id, 'market_analysis', 'completed', 'Market analysis completed')
            if request.form.get('flexSwitchCheck_operations_plan'):
                update_section_progress(bplan_id, 'operations_plan', 'completed', 'Operations plan completed')
            if request.form.get('flexSwitchCheck_requested_fund'):
                update_section_progress(bplan_id, 'requested_fund', 'completed', 'Requested fund completed')
            if request.form.get('flexSwitchCheck_feasibility'):
                update_section_progress(bplan_id, 'feasibility', 'completed', 'Feasibility completed')

            # Update checkboxes
            update_buz_export_plan_checkboxes(
                bool(request.form.get('flexSwitchCheck_client_profile')),
                bool(request.form.get('flexSwitchCheck_business_profile')),
                bool(request.form.get('flexSwitchCheck_business_premises')),
                bool(request.form.get('flexSwitchCheck_market_analysis')),
                bool(request.form.get('flexSwitchCheck_competitors')),
                bool(request.form.get('flexSwitchCheck_operations_plan')),
                bool(request.form.get('flexSwitchCheck_requested_fund')),
                bool(request.form.get('flexSwitchCheck_feasibility')),
                bplan_id
            )

            # ==================== MISSION/VISION & OBJECTIVES ====================
            print("DEBUG: Starting mission/vision and objectives generation...")
            update_section_progress(bplan_id, 'mission_vision', 'in_progress', 'Generating mission and vision...')

            def tracked_mission_vision():
                try:
                    generate_mission_vision_statements(client, query_model, bplan_id, lang)
                    update_section_progress(bplan_id, 'mission_vision', 'completed', 'Mission and vision completed')
                except Exception as e:
                    print(f"Error in mission_vision: {e}")
                    update_section_progress(bplan_id, 'mission_vision', 'error', str(e))

            def tracked_objectives():
                try:
                    get_api_content_objectives(client, query_model, bplan_id, lang)
                    update_section_progress(bplan_id, 'objectives', 'completed', 'Objectives completed')
                except Exception as e:
                    print(f"Error in objectives: {e}")
                    update_section_progress(bplan_id, 'objectives', 'error', str(e))

            update_section_progress(bplan_id, 'objectives', 'in_progress', 'Generating objectives...')

            Thread_mission_vision = threading.Thread(target=tracked_mission_vision)
            Thread_objectives = threading.Thread(target=tracked_objectives)

            Thread_mission_vision.start()
            Thread_objectives.start()

            Thread_mission_vision.join(timeout=45)
            Thread_objectives.join(timeout=30)

            print("DEBUG: Mission/vision and objectives generation completed")

            # Mark entire process as complete
            mark_generation_complete(bplan_id)

            time.sleep(2)

        return redirect(url_for('home_blueprint.export_plan', bplan_id=bplan_id))

    # Render the page normally for GET and after POST (non-PDF)
    return render_template(
        'home/exportplan.html',
        segment='exportplan',
        data_checkboxes=data_export_plan_checkboxes,
        data_bplan=data_get_bplan,
        data_ep=data_export_plan,
        data_fin=data_buz_financial,
        data_staff=data_buz_staff,
        data_bs_total=data_buz_total_salaries,
        data_photo=data_buz_premises_photo,
        data_competitors=data_competitors_preferences,
        data_ex=data_expenses,
        data_x_total=total_expenses,
        data_br=data_buz_resource,
        data_machines=data_fund_machines,
        data_installation=data_fund_installation,
        data_materials=data_fund_materials,
        data_salaries=data_fund_salaries,
        data_ocosts=data_fund_ocosts,
        data_fund_total=data_fund_total,
        data_mkt_segments=data_buz_mkt_segments,
        bplan_id=bplan_id,
        data_projections=data_projections,
        data_total_projections=data_total_projections,
        current_inflation_rate=inflation_rate,
        data_price=data_price_preferences,
        data_service=data_service_preferences,
        data_quality=data_quality_preferences,
        data_location=data_location_preferences,
        data_comp_preferences=data_comp_preferences,
        data_compname=data_buz_competitor,

        # NEW: Operations data for charts
        data_suppliers=data_buz_suppliers,
        data_production=data_buz_production,
        data_distribution=data_buz_distribution,

        data_partners=data_partners,
        data_experiences=data_experiences
    )


# ============================================================
# STEP 3: ADD THIS NEW PROGRESS ENDPOINT
# ============================================================

@blueprint.route('/export_plan/progress/<bplan_id>', methods=['GET'])
@login_required
def export_plan_progress(bplan_id):
    """
    Enhanced progress endpoint with granular status.
    Returns detailed progress for the frontend progress modal.
    """
    progress = get_progress(bplan_id)

    if progress:
        # Calculate percentage
        total_tasks = progress['total_sections'] + 2  # +2 for mission/vision and objectives
        completed_tasks = progress['completed_sections']

        if progress['mission_vision']['status'] == 'completed':
            completed_tasks += 1
        if progress['objectives']['status'] == 'completed':
            completed_tasks += 1

        percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

        return jsonify({
            'found': True,
            'status': progress['status'],
            'percentage': percentage,
            'current_phase': progress['current_phase'],
            'sections': progress['sections'],
            'mission_vision': progress['mission_vision'],
            'objectives': progress['objectives'],
            'completed_sections': progress['completed_sections'],
            'total_sections': progress['total_sections']
        })

    # Fallback to checking database if no active progress
    data_export_plan, status_export_plan = get_export_plan(bplan_id)

    if not data_export_plan:
        return jsonify({'found': False, 'status': 'not_started', 'percentage': 0})

    return jsonify({
        'found': True,
        'status': 'completed',
        'percentage': 100,
        'message': 'Content already generated'
    })


# ============================================================
# PDF EXPORT ROUTE - Add this to your routes.py
# ============================================================

# ============================================================
# PDF EXPORT ROUTE - Add this to your routes.py
# ============================================================

@blueprint.route('/export_plan/pdf/<bplan_id>', methods=['GET'])
@login_required
def export_plan_pdf(bplan_id):
    """Generate and download a professional multi-page PDF business plan."""
    import tempfile
    import os
    from flask import send_file
    from .pdf_generator import generate_business_plan_pdf

    lang = session.get('lang', 'en')

    # Fetch all data
    data_get_bplan, _ = get_bplan(bplan_id)
    data_export_plan, _ = get_export_plan(bplan_id)
    data_buz_financial, _ = get_buz_financial(bplan_id)
    _, data_buz_staff, data_buz_total_salaries = get_buz_staff(bplan_id)
    data_buz_premises_photo, _ = get_buz_premises_photo(bplan_id)
    data_buz_premises_doc, _ = get_buz_premises_doc(bplan_id)  # Documents for appendix
    _, data_expenses, total_expenses = get_expenses(bplan_id)
    _, data_buz_resource, _ = get_buz_resource(bplan_id)
    _, data_fund_installation, _ = get_buz_fund_items(bplan_id, "1")
    _, data_fund_machines, _ = get_buz_fund_items(bplan_id, "2")
    _, data_fund_materials, _ = get_buz_fund_items(bplan_id, "3")
    _, data_fund_salaries, _ = get_buz_fund_items(bplan_id, "4")
    _, data_fund_ocosts, data_fund_total = get_buz_fund_items(bplan_id, "5")
    data_buz_mkt_segments, _ = get_buz_mkt_segments(bplan_id)

    # Feasibility data
    data_buz_product = get_buz_product(bplan_id)[0] or []
    data_buz_expenses = get_buz_expenses(bplan_id)[0] or []
    inflation_data, _ = get_buz_inflation_rate(bplan_id)
    inflation_rate = float(inflation_data[0]['inflation_rate']) if inflation_data else 3.0
    data_projections, data_total_projections = calculate_projections(data_buz_product, data_buz_expenses,
                                                                     inflation_rate=inflation_rate)

    data_comp_preferences, _ = get_selected_preferences_only(bplan_id)
    data_buz_competitor, _ = get_buz_competitor(bplan_id)

    # ===== NEW: Operations data =====
    data_buz_suppliers, _ = get_buz_supplier(bplan_id)
    data_buz_production, _ = get_buz_production(bplan_id)
    data_buz_distribution, _ = get_buz_distribution(bplan_id)

    # Attach products to each supplier
    if data_buz_suppliers:
        for supplier in data_buz_suppliers:
            products, _ = get_products_buz_supplier(supplier.get('supplier_id') or supplier.get('id'))
            supplier['products'] = products if products else []

    # ===== NEW: Client Profile data =====
    data_partners, _ = get_partners(bplan_id)
    data_experiences, _ = get_experiences(bplan_id)

    # Prepare data dictionary
    data = {
        'bplan_id': bplan_id,
        'data_bplan': data_get_bplan,
        'data_ep': data_export_plan,
        'data_fin': data_buz_financial,
        'data_staff': data_buz_staff,
        'data_bs_total': data_buz_total_salaries,
        'data_photo': data_buz_premises_photo,
        'data_bp_doc': data_buz_premises_doc,  # Documents for appendix
        'data_ex': data_expenses,
        'data_x_total': total_expenses,
        'data_br': data_buz_resource,
        'data_machines': data_fund_machines,
        'data_installation': data_fund_installation,
        'data_materials': data_fund_materials,
        'data_salaries': data_fund_salaries,
        'data_ocosts': data_fund_ocosts,
        'data_fund_total': data_fund_total,
        'data_mkt_segments': data_buz_mkt_segments,
        'data_projections': data_projections,
        'data_total_projections': data_total_projections,
        'current_inflation_rate': inflation_rate,
        'data_comp_preferences': data_comp_preferences,
        'data_compname': data_buz_competitor,
        # ===== ADD THESE NEW KEYS =====
        'data_suppliers': data_buz_suppliers,
        'data_production': data_buz_production,
        'data_distribution': data_buz_distribution,
        'data_partners': data_partners,
        'data_experiences': data_experiences,
    }

    # Generate PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_path = tmp.name

    try:
        generate_business_plan_pdf(data, pdf_path, lang=lang)

        business_name = data_get_bplan[0].get('name', 'BusinessPlan') if data_get_bplan else 'BusinessPlan'
        if hasattr(data_get_bplan[0], 'name'):
            business_name = data_get_bplan[0].name
        safe_name = "".join(c for c in business_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')

        return send_file(pdf_path, mimetype='application/pdf', as_attachment=True,
                         download_name=f'{safe_name}_Business_Plan.pdf')
    except Exception as e:
        print(f"PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return f"Error generating PDF: {e}", 500


# ============================================================
# KEEP YOUR EXISTING STATUS ENDPOINT (Optional - for backward compatibility)
# ============================================================

@blueprint.route('/export_plan/status/<bplan_id>', methods=['GET'])
@login_required
def export_plan_status(bplan_id):
    """Check if AI generation is complete for the requested sections"""
    data_export_plan, status_export_plan = get_export_plan(bplan_id)

    if not data_export_plan:
        return jsonify({'complete': False})

    export_data = data_export_plan[0]
    checks = []

    if request.args.get('check_client_profile'):
        client_profile_checks = [
            export_data.client_profile and len(export_data.client_profile.strip()) > 100,
            export_data.client_experiences and len(export_data.client_experiences.strip()) > 50,
            export_data.client_partners and len(export_data.client_partners.strip()) > 50,
            export_data.client_expenses and len(export_data.client_expenses.strip()) > 50,
            export_data.client_employed and len(export_data.client_employed.strip()) > 50
        ]
        checks.append(sum(client_profile_checks) >= 3)

    if request.args.get('check_business_profile'):
        business_profile_checks = [
            export_data.business_profile and len(export_data.business_profile.strip()) > 100,
            export_data.buz_staff and len(export_data.buz_staff.strip()) > 50,
            export_data.buz_resource and len(export_data.buz_resource.strip()) > 50,
            export_data.financial_history and len(export_data.financial_history.strip()) > 50,
            export_data.source_of_funding and len(export_data.source_of_funding.strip()) > 50
        ]
        checks.append(sum(business_profile_checks) >= 3)

    if request.args.get('check_business_premises'):
        checks.append(
            export_data.business_premises and
            len(export_data.business_premises.strip()) > 100
        )

    if request.args.get('check_market_analysis'):
        checks.append(
            export_data.market_analysis and
            len(export_data.market_analysis.strip()) > 100
        )

    if request.args.get('check_operations_plan'):
        operations_checks = [
            export_data.buz_suppliers and len(export_data.buz_suppliers.strip()) > 50,
            export_data.buz_production and len(export_data.buz_production.strip()) > 50,
            export_data.buz_distribution and len(export_data.buz_distribution.strip()) > 50
        ]
        checks.append(all(operations_checks))

    if request.args.get('check_requested_fund'):
        checks.append(
            export_data.requested_fund and
            len(export_data.requested_fund.strip()) > 100
        )

    if request.args.get('check_feasibility'):
        checks.append(
            export_data.feasibility and
            len(export_data.feasibility.strip()) > 100
        )

    is_complete = bool(checks) and all(checks)

    return jsonify({
        'complete': is_complete,
        'checks_performed': len(checks),
        'checks_passed': sum(checks)
    })

@blueprint.route('/exit', methods=['GET', 'POST'])
@login_required
def exit():

    if request.form.get('option') == 'previous':
        return render_template('home/breakeven.html', segment='breakeven')
    # elif request.form.get('option') == 'save':
    #     return render_template('home/exportplan.html', segment='exportplan')
    
@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None



@blueprint.before_request
def make_session_permanent():
    session.permanent = True


# ============================================================
# JADWAPLAN DASHBOARD ROUTE - Fixed Version
# ============================================================
# Add this route to your routes.py file
# This version uses your actual database function names
# ============================================================

@blueprint.route('/dashboard/<bplan_id>')
@login_required
def dashboard(bplan_id):
    """
    Comprehensive Dashboard view for a business plan.
    Fetches all data and calculates KPIs for visualization.
    """
    try:
        # ============================================================
        # FETCH ALL DATA
        # ============================================================

        # Basic Business Plan Info
        data_bplan, _ = get_bplan(bplan_id)
        if not data_bplan:
            if session.get('lang', 'en') == 'ar':
                flash('خطة العمل غير موجودة', 'error')
            else:
                flash('Business plan not found', 'error')
            return redirect(url_for('home_blueprint.index'))

        # Client Profile Data
        data_client_info, _ = get_client_profile(bplan_id)

        # Living Expenses
        expenses_result = get_expenses(bplan_id)
        if expenses_result[0]:
            data_ex = expenses_result[1]
            data_x_total = expenses_result[2] or 0
        else:
            data_ex = []
            data_x_total = 0

        # Partners
        data_partners, _ = get_partners(bplan_id)

        # Experiences
        data_experiences, _ = get_experiences(bplan_id)

        # Staff
        staff_result = get_buz_staff(bplan_id)
        if staff_result[0]:
            data_staff = staff_result[1]
            data_bs_total = staff_result[2] or 0
        else:
            data_staff = []
            data_bs_total = 0

        # Resources
        resource_result = get_buz_resource(bplan_id)
        if resource_result[0]:
            data_br = resource_result[1]
            data_br_total = resource_result[2] or 0
        else:
            data_br = []
            data_br_total = 0

        # Financial History
        data_fin, _ = get_buz_financial(bplan_id)

        # Market Segments
        data_mkt_segments, _ = get_buz_mkt_segments(bplan_id)

        # Competitor Preferences (selected only)
        data_comp_preferences, _ = get_selected_preferences_only(bplan_id, preference_value_check=True)

        # Competitor Names
        data_compname, _ = get_buz_competitor(bplan_id)

        # Suppliers
        data_suppliers, _ = get_buz_supplier(bplan_id)

        # Attach products to suppliers
        if data_suppliers:
            for supplier in data_suppliers:
                supplier_id = supplier.get('supplier_id') if isinstance(supplier, dict) else getattr(supplier,
                                                                                                     'supplier_id',
                                                                                                     None)
                if supplier_id:
                    products, _ = get_products_buz_supplier(supplier_id)
                    supplier['products'] = products if products else []

        # Production
        data_production, _ = get_buz_production(bplan_id)

        # Distribution
        data_distribution, _ = get_buz_distribution(bplan_id)

        # Fund Items (Machinery = 0, Installation = 1, Raw Materials = 2, Salaries = 4, Other = 3)
        machines_result = get_buz_fund_items(bplan_id, 0)
        data_machines = machines_result[1] if machines_result[0] else []

        installation_result = get_buz_fund_items(bplan_id, 1)
        data_installation = installation_result[1] if installation_result[0] else []

        materials_result = get_buz_fund_items(bplan_id, 2)
        data_materials = materials_result[1] if materials_result[0] else []

        salaries_result = get_buz_fund_items(bplan_id, 4)
        data_salaries = salaries_result[1] if salaries_result[0] else []

        ocosts_result = get_buz_fund_items(bplan_id, 3)
        data_ocosts = ocosts_result[1] if ocosts_result[0] else []

        # Get total fund
        fund_result = get_buz_fund_items(bplan_id, 0)  # Any type to get total
        data_fund_total = fund_result[2] if fund_result[0] else 0

        # Products for feasibility
        data_products, _ = get_buz_product(bplan_id)

        # Operating Expenses for feasibility
        data_op_expenses, _ = get_buz_expenses(bplan_id)

        # Inflation Rate
        inflation_result, _ = get_buz_inflation_rate(bplan_id)
        current_inflation_rate = inflation_result[0].get('inflation_rate', 3.0) if inflation_result else 3.0

        # Calculate projections
        data_projections, data_total_projections = calculate_projections(
            data_products if data_products else [],
            data_op_expenses if data_op_expenses else [],
            float(current_inflation_rate or 0)  # Convert Decimal to float
        )
        # Business Premises Photos
        data_photo, _ = get_buz_premises_photo(bplan_id)

        # ============================================================
        # HELPER FUNCTION FOR SAFE ATTRIBUTE ACCESS
        # ============================================================
        def safe_get(obj, key, default=None):
            if obj is None:
                return default
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # ============================================================
        # EXTRACT BASIC INFO
        # ============================================================
        bplan = data_bplan[0] if isinstance(data_bplan, list) and data_bplan else data_bplan
        client_info = data_client_info[0] if isinstance(data_client_info, list) and data_client_info else (
                    data_client_info or {})

        business_name = safe_get(bplan, 'name', 'Business Plan')
        completion = safe_get(bplan, 'completion', 0) or 0
        currency = safe_get(bplan, 'buz_currency', 'USD') or 'USD'
        creation_date = safe_get(bplan, 'creation_date', None)
        created_date = creation_date.strftime('%Y-%m-%d') if creation_date else 'N/A'

        # Industry mapping
        industry_code = str(safe_get(bplan, 'industry', ''))
        is_arabic = session.get('lang', 'en') == 'ar'
        industry_map_en = {'1': 'Agriculture', '2': 'Manufacturing', '3': 'Technology',
                           '4': 'Craft', '5': 'Hospitality', '6': 'Services', '7': 'Trade'}
        industry_map_ar = {'1': 'الزراعة', '2': 'التصنيع', '3': 'التكنولوجيا',
                           '4': 'الحرف اليدوية', '5': 'الضيافة', '6': 'الخدمات', '7': 'التجارة'}
        industry = (industry_map_ar if is_arabic else industry_map_en).get(industry_code, 'Other')

        # Status mapping
        status_code = str(safe_get(bplan, 'status', ''))
        status_map_en = {'1': 'New', '2': 'Existing', '': 'Draft'}
        status_map_ar = {'1': 'جديد', '2': 'قائم', '': 'مسودة'}
        status = (status_map_ar if is_arabic else status_map_en).get(status_code, 'Draft')

        # ============================================================
        # CALCULATE KPIs
        # ============================================================

        # Client Profile KPIs
        total_experience_years = 0
        experience_fields = set()
        if data_experiences:
            for exp in data_experiences:
                years = safe_get(exp, 'years_of_experience', 0) or 0
                try:
                    total_experience_years += int(years)
                except (ValueError, TypeError):
                    pass
                field = safe_get(exp, 'field', '')
                if field:
                    experience_fields.add(field)

        # Owner share calculation
        partners_total_shares = 0
        if data_partners:
            for p in data_partners:
                shares = safe_get(p, 'partner_shares', 0) or 0
                try:
                    partners_total_shares += int(shares)
                except (ValueError, TypeError):
                    pass
        owner_share = 100 - partners_total_shares

        # Monthly expenses
        monthly_expenses = round(data_x_total / 12, 2) if data_x_total else 0

        # Staff KPIs
        staff_count = len(data_staff) if data_staff else 0
        fulltime_count = 0
        parttime_count = 0
        if data_staff:
            for s in data_staff:
                work_time = str(safe_get(s, 'work_time', '')).lower()
                if 'full' in work_time:
                    fulltime_count += 1
                else:
                    parttime_count += 1

        # Resources total
        resources_total = data_br_total

        # Suppliers KPIs
        suppliers_count = len(data_suppliers) if data_suppliers else 0
        total_products = 0
        if data_suppliers:
            for s in data_suppliers:
                products = safe_get(s, 'products', []) or []
                total_products += len(products)

        # Capacity utilization
        capacity_utilization = 0
        current_capacity = 0
        max_capacity = 0
        if data_production:
            prod = data_production[0] if isinstance(data_production, list) else data_production
            try:
                current_capacity = float(safe_get(prod, 'current_capacity', 0) or 0)
                max_capacity = float(safe_get(prod, 'max_expected_capacity', 0) or 1)
                if max_capacity > 0:
                    capacity_utilization = round((current_capacity / max_capacity) * 100, 1)
            except (ValueError, TypeError):
                pass

        # Distribution channels
        distribution_count = len(data_distribution) if data_distribution else 0

        # Market segments
        segments_count = len(data_mkt_segments) if data_mkt_segments else 0

        # Fund breakdown
        def sum_total_cost(items):
            total = 0
            if items:
                for item in items:
                    try:
                        total += float(safe_get(item, 'total_cost', 0) or 0)
                    except (ValueError, TypeError):
                        pass
            return total

        machines_total = sum_total_cost(data_machines)
        installation_total = sum_total_cost(data_installation)
        materials_total = sum_total_cost(data_materials)
        salaries_total = sum_total_cost(data_salaries)
        other_costs_total = sum_total_cost(data_ocosts)

        # Feasibility KPIs
        year1_revenue = 0
        year5_revenue = 0
        year1_profit = 0
        year5_profit = 0
        year5_margin = 0
        revenue_growth = 0

        if data_total_projections and data_total_projections.get('years'):
            years_data = data_total_projections['years']
            if len(years_data) >= 2:
                year1_revenue = years_data[1].get('grand_total_revenue', 0) if len(years_data) > 1 else 0
                year1_profit = years_data[1].get('profit', 0) if len(years_data) > 1 else 0
            if len(years_data) >= 6:
                year5_revenue = years_data[5].get('grand_total_revenue', 0)
                year5_profit = years_data[5].get('profit', 0)
                year5_margin = years_data[5].get('margin', 0)
            if year1_revenue > 0 and year5_revenue > 0:
                revenue_growth = round(((year5_revenue - year1_revenue) / year1_revenue) * 100, 1)

        # ============================================================
        # PREPARE CHART DATA (JSON-serializable)
        # ============================================================

        # Experiences Chart Data
        experiences_chart = []
        if data_experiences:
            for exp in data_experiences:
                try:
                    years_val = int(safe_get(exp, 'years_of_experience', 0) or 0)
                except (ValueError, TypeError):
                    years_val = 0
                experiences_chart.append({
                    'field': safe_get(exp, 'field', 'N/A'),
                    'workplace': safe_get(exp, 'workplace', 'N/A'),
                    'years': years_val
                })

        # Ownership Chart Data
        ownership_chart = []
        client_name = safe_get(client_info, 'full_name', '') or 'Owner'
        ownership_chart.append({'name': client_name if client_name else 'Owner', 'shares': owner_share})
        if data_partners:
            for p in data_partners:
                try:
                    shares_val = int(safe_get(p, 'partner_shares', 0) or 0)
                except (ValueError, TypeError):
                    shares_val = 0
                ownership_chart.append({
                    'name': safe_get(p, 'partner_name', 'Partner'),
                    'shares': shares_val
                })

        # Living Expenses Chart Data
        expenses_chart = []
        if data_ex:
            for e in data_ex:
                try:
                    val = float(safe_get(e, 'total_value', safe_get(e, 'value', 0)) or 0)
                except (ValueError, TypeError):
                    val = 0
                expenses_chart.append({
                    'type': safe_get(e, 'living_expenses', 'Other'),
                    'value': val
                })

        # Staff Chart Data
        staff_chart = []
        staff_positions = {}
        if data_staff:
            for s in data_staff:
                pos = safe_get(s, 'staff_position', 'Other')
                try:
                    salary = float(safe_get(s, 'staff_salary', 0) or 0)
                except (ValueError, TypeError):
                    salary = 0
                if pos in staff_positions:
                    staff_positions[pos] += salary
                else:
                    staff_positions[pos] = salary
            for pos, salary in staff_positions.items():
                staff_chart.append({'position': pos, 'salary': salary})

        # Resources Chart Data
        resources_chart = []
        if data_br:
            for r in data_br:
                try:
                    val = float(safe_get(r, 'resource_value', 0) or 0)
                except (ValueError, TypeError):
                    val = 0
                resources_chart.append({
                    'type': safe_get(r, 'resource_subtype', safe_get(r, 'resource_type', 'Other')),
                    'value': val
                })

        # Financial History Chart Data
        financial_history_chart = []
        if data_fin:
            for f in data_fin:
                try:
                    sales = float(safe_get(f, 'financial_sales', 0) or 0)
                    profit = float(safe_get(f, 'financial_profit', 0) or 0)
                except (ValueError, TypeError):
                    sales = 0
                    profit = 0
                financial_history_chart.append({
                    'year': str(safe_get(f, 'financial_year', '')),
                    'sales': sales,
                    'profit': profit
                })

        # Market Segments Chart Data
        segments_chart = []
        if data_mkt_segments:
            for s in data_mkt_segments:
                try:
                    pct = float(safe_get(s, 'segment_percentage', 0) or 0)
                except (ValueError, TypeError):
                    pct = 0
                segments_chart.append({
                    'name': safe_get(s, 'segment_name', 'Other'),
                    'percentage': pct
                })

        # Competitive Analysis Chart Data
        competitive_chart = {'labels': [], 'business': [], 'comp1': [], 'comp2': [], 'comp3': []}
        comp_names = {'business': business_name, 'comp1': 'Competitor 1', 'comp2': 'Competitor 2',
                      'comp3': 'Competitor 3'}
        if data_compname:
            cn = data_compname[0] if isinstance(data_compname, list) else data_compname
            comp_names['comp1'] = safe_get(cn, 'competitor_name_1st', 'Competitor 1') or 'Competitor 1'
            comp_names['comp2'] = safe_get(cn, 'competitor_name_2nd', 'Competitor 2') or 'Competitor 2'
            comp_names['comp3'] = safe_get(cn, 'competitor_name_3rd', 'Competitor 3') or 'Competitor 3'

        if data_comp_preferences:
            for pref in data_comp_preferences:
                competitive_chart['labels'].append(safe_get(pref, 'preference', ''))
                try:
                    competitive_chart['business'].append(float(safe_get(pref, 'preference_value', 0) or 0))
                    competitive_chart['comp1'].append(float(safe_get(pref, 'competitor1_value', 0) or 0))
                    competitive_chart['comp2'].append(float(safe_get(pref, 'competitor2_value', 0) or 0))
                    competitive_chart['comp3'].append(float(safe_get(pref, 'competitor3_value', 0) or 0))
                except (ValueError, TypeError):
                    competitive_chart['business'].append(0)
                    competitive_chart['comp1'].append(0)
                    competitive_chart['comp2'].append(0)
                    competitive_chart['comp3'].append(0)

        competitive_chart['names'] = comp_names

        # Suppliers Radar Chart Data
        suppliers_chart = []
        if data_suppliers:
            for sup in data_suppliers[:4]:  # Max 4 suppliers for radar
                products = safe_get(sup, 'products', []) or []

                # Convert quality to score
                quality_map = {'High quality': 5, 'Good quality': 4, 'Consistent': 3, 'Commercial': 2}
                quality = quality_map.get(safe_get(sup, 'quality', ''), 3)

                # Convert years to score
                years_str = str(safe_get(sup, 'years_of_collaboration', '1-3'))
                years_map = {'10+': 5, '7-10': 4, '5-7': 3, '3-5': 2, '1-3': 1, '0-1': 0.5}
                years = years_map.get(years_str, 1)

                # Calculate average price score from products
                price_map = {'Very low': 5, 'Affordable': 4, 'Moderate': 3, 'Expensive': 2, 'Very expensive': 1}
                avg_price = 3
                if products:
                    price_scores = [price_map.get(safe_get(p, 'prices', 'Moderate'), 3) for p in products]
                    avg_price = sum(price_scores) / len(price_scores)

                # Calculate average quantity consistency from products
                qty_map = {'Consistent': 5, 'Inconsistent': 2}
                avg_qty = 3
                if products:
                    qty_scores = [qty_map.get(safe_get(p, 'quantity', 'Consistent'), 3) for p in products]
                    avg_qty = sum(qty_scores) / len(qty_scores)

                suppliers_chart.append({
                    'name': safe_get(sup, 'supplier_name', 'Supplier'),
                    'quality': quality,
                    'years': years,
                    'price': round(avg_price, 1),
                    'consistency': round(avg_qty, 1)
                })

        # Fund Allocation Chart Data
        fund_chart = [
            {'category': 'Machinery' if not is_arabic else 'الآلات', 'value': machines_total},
            {'category': 'Installation' if not is_arabic else 'التركيب', 'value': installation_total},
            {'category': 'Materials' if not is_arabic else 'المواد', 'value': materials_total},
            {'category': 'Salaries' if not is_arabic else 'الرواتب', 'value': salaries_total},
            {'category': 'Other Costs' if not is_arabic else 'تكاليف أخرى', 'value': other_costs_total}
        ]
        # Filter out zero values
        fund_chart = [f for f in fund_chart if f['value'] > 0]

        # Projections Chart Data (5 years)
        projections_chart = {'years': [], 'revenue': [], 'costs': [], 'profit': [], 'margin': []}
        if data_total_projections and data_total_projections.get('years'):
            year_labels = ['Current', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
            for i, year_data in enumerate(data_total_projections['years']):
                if i < len(year_labels):
                    projections_chart['years'].append(year_labels[i])
                    projections_chart['revenue'].append(year_data.get('grand_total_revenue', 0))
                    total_costs = year_data.get('grand_total_cost', 0) + year_data.get('total_operating_expenses', 0)
                    projections_chart['costs'].append(total_costs)
                    projections_chart['profit'].append(year_data.get('profit', 0))
                    projections_chart['margin'].append(year_data.get('margin', 0))

        # ============================================================
        # RENDER TEMPLATE
        # ============================================================
        return render_template('home/dashboard.html',
                               segment='dashboard',
                               bplan_id=bplan_id,

                               # Basic Info
                               business_name=business_name,
                               completion=completion,
                               currency=currency,
                               created_date=created_date,
                               industry=industry,
                               status=status,

                               # KPIs
                               kpis={
                                   'total_fund': data_fund_total,
                                   'year1_revenue': year1_revenue,
                                   'year5_revenue': year5_revenue,
                                   'year1_profit': year1_profit,
                                   'year5_profit': year5_profit,
                                   'year5_margin': year5_margin,
                                   'revenue_growth': revenue_growth,
                                   'staff_count': staff_count,
                                   'fulltime_count': fulltime_count,
                                   'parttime_count': parttime_count,
                                   'total_salaries': data_bs_total,
                                   'total_experience': total_experience_years,
                                   'experience_fields': len(experience_fields),
                                   'owner_share': owner_share,
                                   'monthly_expenses': monthly_expenses,
                                   'yearly_expenses': data_x_total,
                                   'resources_total': resources_total,
                                   'suppliers_count': suppliers_count,
                                   'total_products': total_products,
                                   'capacity_utilization': capacity_utilization,
                                   'current_capacity': current_capacity,
                                   'max_capacity': max_capacity,
                                   'distribution_count': distribution_count,
                                   'segments_count': segments_count,
                                   'inflation_rate': current_inflation_rate,
                               },

                               # Chart Data (JSON serializable)
                               charts={
                                   'experiences': experiences_chart,
                                   'ownership': ownership_chart,
                                   'expenses': expenses_chart,
                                   'staff': staff_chart,
                                   'resources': resources_chart,
                                   'financial_history': financial_history_chart,
                                   'segments': segments_chart,
                                   'competitive': competitive_chart,
                                   'suppliers': suppliers_chart,
                                   'fund': fund_chart,
                                   'projections': projections_chart,
                               },

                               # Raw data for tables (if needed)
                               data={
                                   'staff': data_staff,
                                   'partners': data_partners,
                                   'experiences': data_experiences,
                                   'suppliers': data_suppliers,
                                   'production': data_production,
                                   'distribution': data_distribution,
                               }
                               )

    except Exception as e:
        import traceback
        print(f"Dashboard error: {e}")
        traceback.print_exc()
        if session.get('lang', 'en') == 'ar':
            flash('حدث خطأ أثناء تحميل لوحة التحكم', 'error')
        else:
            flash('Error loading dashboard', 'error')
        return redirect(url_for('home_blueprint.index'))