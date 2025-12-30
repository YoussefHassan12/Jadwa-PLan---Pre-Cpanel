def insert_bplan(var_name, var_industry, var_sector, var_subsector, var_currency, var_status):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        var_email = session.get('username')

        sql = "INSERT INTO public.bplan(Name,Email,industry,buz_sector,buz_subsector, buz_currency,Creation_date,Status,Completion, complete_client_profile, complete_business_profile, complete_business_premises, complete_market_analysis, complete_competitors, complete_operations_plan, complete_requested_fund, complete_feasibility ) " \
              " VALUES ('{}','{}','{}','{}','{}','{}',current_timestamp,'{}',0, '0', '0', '0', '0', '0', '0', '0', '0')".format(
            var_name, var_email, var_industry, var_sector, var_subsector, var_currency, var_status)
        cur.execute(sql)

        sql = "SELECT MAX(bplan_id) FROM public.bplan"
        cur.execute(sql)
        bplan_id = cur.fetchall()

        sql = "INSERT INTO public.client_info(bplan_id, full_name, client_avatar, gender, marital_status, number_of_children, nationality, dob, education_level, years_of_experience, education_major, specialty, education_institution) " \
              " VALUES ({}, '', 'avatar.png', 1, 1, 0, 1, to_date('2000-01-01','YYYY-MM-DD'), 1, 0, '', '', '');".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.employed(bplan_id, emp_where, emp_job_hold, emp_location, emp_duration, emp_monthly_income) " \
              " VALUES ({}, '', '', '', '', 0);".format(bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.side_business(bplan_id, buz_name, buz_industry, buz_location, buz_duration, buz_monthly_income) " \
              "VALUES ({}, '', 1, '', '', 0);".format(bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_info(bplan_id, buz_name, buz_address, buz_est_date, buz_legal_status, buz_model, product_services) " \
              "VALUES ({}, '{}', '', to_date('2000-01-01','YYYY-MM-DD'), '', '[1]', '');".format(bplan_id[0][0],
                                                                                                 var_name)
        cur.execute(sql)

        sql = "INSERT INTO public.buz_mkt_analysis (bplan_id, segment_name, business_model, segment_percentage, market_channel, age_min, age_max, income_min, income_max, male_rate, female_rate, education, occupation, life_stage, location, preferences, industry, company_size) VALUES ({}, '', 'B2B', 0, '[]', 20, 80, 500, 8000, 49, 51, '[]', '[]', '[]', '', '', '', '');".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_preferences (SELECT {}, preference_id, category_id, preference, 0, 0, 0, 0, 0, 0 from public.lst_preferences);".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_competitor(bplan_id, competitor_name_1st, competitor_name_2nd, competitor_name_3rd) VALUES ({}, '', '', '');".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_operation_plan(bplan_id, enhance_production, customer_support) VALUES ({}, '[]', '[]');".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_feasibility(bplan_id, first_year, second_year, third_year, fourth_year, fifth_year, annual_growth, inflation_rate, depreciation) VALUES ({}, 0, 0, 0, 0, 0, 0, 0, 0);".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_fund_details( bplan_id, project_objectives, project_purposes, fund_type, amount, equity, interest_rate, period, grace_period) VALUES ({}, '[]', '[]', '', 0, 0, 0, 0, 0);".format(
            bplan_id[0][0])
        cur.execute(sql)

        sql = "INSERT INTO public.buz_export_plan(bplan_id, client_avatar, full_name, client_gender, client_profile, client_experiences, client_partners, client_expenses, client_employed, side_business, business_profile, buz_staff, buz_resource, business_premises, market_analysis, buz_suppliers, buz_production, enhance_production, buz_distribution, customer_support, requested_fund, feasibility)	\
        VALUES ({}, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');".format(
            bplan_id[0][0])
        cur.execute(sql)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return ("*", error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
    return


def new_plan():
    if request.form.get('option') == 'create':
        insert_bplan(request.form.get('brand_name'),
                     request.form.get('choices_industry'),
                     request.form.get('choices_sector'),
                     request.form.get('choices_subsector'),
                     request.form.get('choices_currency'),
                     request.form.get('choices_status'))

        results, status_bplan = get_bplan_list()
        if '*' in results:
            return render_template('accounts/login.html', msg=status_bplan)
        else:
            return render_template('home/index.html', segment='index', data=results)

    elif request.form.get('option') == 'cancel':
        results, status = get_bplan_list()
        if '*' in results:
            return render_template('accounts/login.html', msg=status)
        else:
            return render_template('home/index.html', segment='index', data=results)
    else:
        data_lst_industries, status_lst_industries = get_lst_industries()
        data_lst_sectors, status2 = get_lst_sectors()
        if '*' in data_lst_industries or '*' in data_lst_sectors:
            return render_template('accounts/login.html', msg=status_lst_industries)
        else:
            return render_template('home/newplan.html',
                                   lst_industries=data_lst_industries,
                                   lst_sectors=data_lst_sectors)


def clientprofile(bplan_id):
    # if request.method == 'GET':
    #     print('GET',request.args.get('partner'))
    #     var1 = request.args
    #     for key, value in var1.items():
    #         print(key, value)
    #     # request.args.get('')

    if request.method == 'POST':
        if request.form.get('flexSwitchCheck_employed') == None:
            update_employed('', '', '', '', 0, bplan_id)
        else:
            update_employed(request.form.get('employed_where'),
                            request.form.get('employed_job_hold'),
                            request.form.get('employed_location'),
                            request.form.get('employed_duration'),
                            request.form.get('employed_monthly_income'),
                            bplan_id)

        if request.form.get('flexSwitchCheck_business') == None:
            update_side_business('', 0, '', '', 0, bplan_id)
        else:
            update_side_business(request.form.get('business_name'),
                                 request.form.get('choices_industry'),
                                 request.form.get('business_location'),
                                 request.form.get('business_duration'),
                                 request.form.get('business_monthly_income'),
                                 bplan_id)

        update_bool = False
        if request.form.get('partner_delete') != None: partner_delete(request.form.get('partner_delete'))
        if request.form.get('partner_add') != None:
            update_bool = True
            partner_add(request.form.get('partner_add'),
                        request.form.get('partner_name'),
                        request.form.get('choice_partner_relation'),
                        request.form.get('partner_experience'),
                        request.form.get('partner_years_of_experience'),
                        request.form.get('partner_role'),
                        request.form.get('partner_shares')
                        )

        if request.form.get('experience_delete') != None: experience_delete(request.form.get('experience_delete'))
        if request.form.get('experiences_add') != None:
            update_bool = True
            experiences_add(request.form.get('experiences_add'),
                            request.form.get('experience_field'),
                            request.form.get('years_of_experience'),
                            request.form.get('experience_workplace'))
        if request.form.get('expense_delete') != None: expense_delete(request.form.get('expense_delete'))
        if request.form.get('expenses_add') != None:
            update_bool = True
            expenses_add(request.form.get('expenses_add'),
                         request.form.get('choices_living_expenses'),
                         request.form.get('expense_value'),
                         request.form.get('choice_expense_unit'))
        if update_bool:
            file = request.files['fileAvatar']
            if file and allowed_file(file.filename):
                filename = bplan_id + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join('apps/static/uploads', filename))
            else:
                filename = 'avatar.png'
            update_client_profile(request.form.get('full_name'), filename,
                                  request.form.get('choice_gender'),
                                  request.form.get('choice_status'),
                                  request.form.get('number_of_children'),
                                  request.form.get('choice_nationality'),
                                  request.form.get('date_of_birth'),
                                  request.form.get('choice_education_level'),
                                  request.form.get('years_experience'),
                                  request.form.get('education_major'),
                                  request.form.get('specialty'),
                                  request.form.get('education_institution'),
                                  bplan_id)

        if request.form.get('action') == "save":
            update_bplan_completion('complete_client_profile', bplan_id)
            file = request.files['fileAvatar']
            if file and allowed_file(file.filename):
                filename = bplan_id + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join('apps/static/uploads', filename))
            else:
                filename = 'avatar.png'
            update_client_profile(request.form.get('full_name'), filename,
                                  request.form.get('choice_gender'),
                                  request.form.get('choice_status'),
                                  request.form.get('number_of_children'),
                                  request.form.get('choice_nationality'),
                                  request.form.get('date_of_birth'),
                                  request.form.get('choice_education_level'),
                                  request.form.get('years_experience'),
                                  request.form.get('education_major'),
                                  request.form.get('specialty'),
                                  request.form.get('education_institution'),
                                  bplan_id)
            return redirect(url_for('home_blueprint.bussiness_profile', bplan_id=bplan_id))

    data_completion, status_completion = get_completion(bplan_id)
    data_client_info, status_client_info = get_client_profile(bplan_id)
    data_partners, status_partners = get_partners(bplan_id)
    data_experiences, status_experiences = get_experiences(bplan_id)
    status_expenses, data_expenses, total_expenses = get_expenses(bplan_id)
    data_employed, status_employed = get_employed(bplan_id)
    data_side_business, status_side_business = get_side_business(bplan_id)
    data_lst_nationalities, status_lst_nationalities = get_lst_nationalities()
    data_lst_industries, status_lst_industries = get_lst_industries()

    return render_template('home/clientprofile.html', segment='clientprofile',
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
                           bplan_id=bplan_id)

#for the photo
def get_bplan_list():
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT bplan_id, name, email, industry, buz_sector, buz_subsector, buz_currency, creation_date, status, completion " \
              " FROM public.bplan order by Creation_date desc;"
        cur.execute(sql)
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


def operations_plan(bplan_id):
    if request.method == 'POST':
        if request.form.get('supplier_add') != None:
            supplier_add(request.form.get('supplier_add'),
                         request.form.get('supplier_name'),
                         request.form.get('Services'),
                         request.form.get('choice_collaboration'),
                         request.form.get('choice_performance_type'),
                         request.form.get('choice_prices'),
                         request.form.get('choice_quantity'),
                         request.form.get('choice_quality'),
                         request.form.get('choice_customer_service'))
        # if request.form.get('supplier_product_delete') != None:
        #     supplier_product_delete(request.form.get('supplier_product_delete'))
        if request.form.get('supplier_product_delete') != None:
            # Split the combined supplier_id and product_id
            ids = request.form['supplier_product_delete'].split('_')
            if len(ids) == 2:
                success, message = supplier_product_delete(ids[0], ids[1])
                if not success:
                    flash(f'Error deleting product: {message}', 'error')
            else:
                flash('Invalid product identifier', 'error')

        if request.form.get('production_add') != None:
            production_add(request.form.get('production_add'), '',
                           #    request.form.get('choice_allocated_resources'),
                           request.form.get('choice_production_unit'),
                           request.form.get('choice_time_frame'),
                           request.form.get('current_capacity'),
                           request.form.get('max_expected_capacity'))
        if request.form.get('production_delete') != None:
            production_delete(request.form.get('production_delete'))
        if request.form.get('distribution_add') != None:
            distribution_add(request.form.get('distribution_add'),
                             request.form.get('distributor_name'),
                             request.form.get('choice_type'),
                             request.form.get('dis_collaboration_years'))
        if request.form.get('distribution_delete') != None:
            distribution_delete(request.form.get('distribution_delete'))

        if request.form.get('action') == 'save':
            update_bplan_completion('complete_operations_plan', bplan_id)
            update_buz_operation_plan(str(request.form.getlist('choice_enhance')).replace("'", ""),
                                      str(request.form.getlist('choice_customer_support')).replace("'", ""),
                                      bplan_id)

            return redirect(url_for('home_blueprint.requested_fund', bplan_id=bplan_id))
        # ✅ Redirect after any POST to prevent duplicate insertions on refresh
        return redirect(url_for('home_blueprint.operations_plan', bplan_id=bplan_id))

    data_completion, status_completion = get_completion(bplan_id)
    data_buz_supplier, status_buz_supplier = get_buz_supplier(bplan_id)
    data_buz_production, status_buz_production = get_buz_production(bplan_id)
    data_buz_distribution, status_buz_distribution = get_buz_distribution(bplan_id)
    # status_buz_resource, data_buz_resource, data_buz_total_resources = get_buz_resource(bplan_id)
    data_buz_operation_plan, status_buz_operation_plan = get_buz_operation_plan(bplan_id)

    return render_template('home/operationsplan.html', segment='operationsplan',
                           data_comp=data_completion,
                           data_bs=data_buz_supplier,
                           data_bp=data_buz_production,
                           data_bd=data_buz_distribution,
                           #    data_res = data_buz_resource,
                           data_op=data_buz_operation_plan,
                           bplan_id=bplan_id)

def get_buz_supplier(bplan_id):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "select * from public.buz_suppliers where bplan_id ={};".format(bplan_id)
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
            ids = request.form['supplier_product_delete'].split('_')
            if len(ids) == 2:
                success, message = supplier_product_delete(ids[0], ids[1])
                if not success:
                    flash(f'Error deleting product: {message}', 'error')
                else:
                    flash('Product deleted successfully', 'success')
            else:
                flash('Invalid product identifier', 'error')

        # Handle Supplier Deletion
        elif request.form.get('supplier_delete') is not None:
            success, message = supplier_delete(request.form['supplier_delete'])
            if not success:
                flash(f'Error deleting supplier: {message}', 'error')
            else:
                flash(message, 'success')

        # Production handlers (unchanged)
        if request.form.get('production_add') is not None:
            production_add(
                request.form['production_add'], '',
                request.form['choice_production_unit'],
                request.form['choice_time_frame'],
                request.form['current_capacity'],
                request.form['max_expected_capacity']
            )

        if request.form.get('production_delete') is not None:
            production_delete(request.form['production_delete'])

        # Distribution handlers (unchanged)
        if request.form.get('distribution_add') is not None:
            distribution_add(
                request.form['distribution_add'],
                request.form['distributor_name'],
                request.form['choice_type'],
                request.form['dis_collaboration_years']
            )

        if request.form.get('distribution_delete') is not None:
            distribution_delete(request.form['distribution_delete'])

        if request.form.get('action') == 'save':
            update_bplan_completion('complete_operations_plan', bplan_id)
            update_buz_operation_plan(
                str(request.form.getlist('choice_enhance')).replace("'", ""),
                str(request.form.getlist('choice_customer_support')).replace("'", ""),
                bplan_id
            )
            return redirect(url_for('home_blueprint.requested_fund', bplan_id=bplan_id))

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



works
def operations_plan(bplan_id):
    if request.method == 'POST':
        # Handle Supplier Addition (Basic Info Only)
        if request.form.get('supplier_add') is not None:
            # First add supplier basic info
            supplier_id, error = supplier_add(
                bplan_id=bplan_id,  # ✅ Correct usage
                supplier_name=request.form['supplier_name'],
                years_of_collaboration=request.form['choice_collaboration'],
                # performance_type=request.form['choice_performance_type'],
                performance_type=request.form.get('choice_performance_type', 'N/A'),
                quality=request.form['choice_quality'],
                customer_service=request.form['choice_customer_service']
            )

            if error:
                flash(f'Error adding supplier: {error}', 'error')
            else:
                pass
                # Then add the first product for this supplier
                # product_id, error = supplier_product_add(
                #     supplier_id=supplier_id,
                #     product_service=request.form['product_service'], #product_service=request.form['Services'],
                #     product_service=request.form.get('product_service'),
                #     prices=request.form['choice_prices'],
                #     quantity=request.form['choice_quantity']
                # )
                if error:
                    flash(f'Error adding product: {error}', 'error')

        # Handle Product Deletion
        elif request.form.get('supplier_product_delete') is not None:
            ids = request.form['supplier_product_delete'].split('_')
            if len(ids) == 2:
                success, message = supplier_product_delete(ids[0], ids[1])
                if not success:
                    flash(f'Error deleting product: {message}', 'error')
                else:
                    flash('Product deleted successfully', 'success')
            else:
                flash('Invalid product identifier', 'error')

        # Handle Supplier Deletion (will cascade to products)
        elif request.form.get('supplier_delete') is not None:
            success, message = supplier_delete(request.form['supplier_delete'])
            if not success:
                flash(f'Error deleting supplier: {message}', 'error')
            else:
                flash(message, 'success')

        # [Keep your existing production and distribution handlers]
        if request.form.get('production_add') is not None:
            production_add(
                request.form['production_add'], '',
                request.form['choice_production_unit'],
                request.form['choice_time_frame'],
                request.form['current_capacity'],
                request.form['max_expected_capacity']
            )

        if request.form.get('production_delete') is not None:
            production_delete(request.form['production_delete'])

        if request.form.get('distribution_add') is not None:
            distribution_add(
                request.form['distribution_add'],
                request.form['distributor_name'],
                request.form['choice_type'],
                request.form['dis_collaboration_years']
            )

        if request.form.get('distribution_delete') is not None:
            distribution_delete(request.form['distribution_delete'])

        if request.form.get('action') == 'save':
            update_bplan_completion('complete_operations_plan', bplan_id)
            update_buz_operation_plan(
                str(request.form.getlist('choice_enhance')).replace("'", ""),
                str(request.form.getlist('choice_customer_support')).replace("'", ""),
                bplan_id
            )
            return redirect(url_for('home_blueprint.requested_fund', bplan_id=bplan_id))

        return redirect(url_for('home_blueprint.operations_plan', bplan_id=bplan_id))

    # GET Request Handling
    data_completion, status_completion = get_completion(bplan_id)
    data_buz_supplier, status_buz_supplier = get_buz_supplier(bplan_id)  # Only suppliers

    # Fallbacks to prevent template errors
    if data_buz_supplier is None:
        data_buz_supplier = []

    data_buz_production, status_buz_production = get_buz_production(bplan_id)
    data_buz_distribution, status_buz_distribution = get_buz_distribution(bplan_id)
    data_buz_operation_plan, status_buz_operation_plan = get_buz_operation_plan(bplan_id)

    print("Suppliers data:", data_buz_supplier)  # Check your console/flask logs

    return render_template('home/operationsplan.html',
                           segment='operationsplan',
                           data_comp=data_completion,
                           data_bs=data_buz_supplier,  # This contains only supplier data
                           data_bp=data_buz_production,
                           data_bd=data_buz_distribution,
                           data_op=data_buz_operation_plan,
                           bplan_id=bplan_id)
