@blueprint.route('/export_plan/<bplan_id>', methods=['GET', 'POST'])
@login_required
def export_plan(bplan_id):

    import json
    import os
    import re

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
    data_price_preferences, status_price_preferences = get_preferences (bplan_id, '1', False)
    data_service_preferences, status_service_preferences = get_preferences (bplan_id, '2', False)
    data_quality_preferences, status_quality_preferences = get_preferences (bplan_id, '3', False)
    data_location_preferences, status_location_preferences = get_preferences (bplan_id, '4', False)
    data_comp_preferences, status_comp_preferences = get_selected_preferences_only(bplan_id)
    data_buz_competitor, _ = get_buz_competitor(bplan_id)

    # POST request handling
    if request.method == 'POST':
        if request.form.get('action') == 'screenshot_pdf':
            try:
                import tempfile
                from PIL import Image
                import img2pdf

                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()

                    # Set viewport size for full page capture
                    page.set_viewport_size({"width": 1200, "height": 800})

                    # Generate URL
                    screenshot_url = f"http://localhost:5000/export_plan/{bplan_id}?screenshot=true"

                    # Navigate to page
                    page.goto(screenshot_url)

                    # Wait for page to load
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)  # Additional wait

                    # Take full page screenshot
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        screenshot_path = tmp.name

                    page.screenshot(path=screenshot_path, full_page=True)
                    browser.close()

                    # Convert to PDF
                    image = Image.open(screenshot_path)
                    pdf_bytes = img2pdf.convert(image.filename)

                    # Clean up
                    os.remove(screenshot_path)

                    response = make_response(pdf_bytes)
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Disposition'] = f'attachment; filename=export_plan_{bplan_id}.pdf'

                    return response

            except Exception as e:
                print(f"Playwright screenshot error: {e}")
                return f"Error generating screenshot: {e}", 500

        # ---------------------- GENERATE OPTION ----------------------
        if request.form.get('action') == 'generate':
            import threading
            import time
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)
            query_model = "gpt-4o-mini"

            time.sleep(1)
            # Start all your threads (unchanged)
            # Start all your threads with proper tracking
            all_threads = []

            if request.form.get('flexSwitchCheck_client_profile') is not None:
                Thread_client_info = threading.Thread(target=get_api_content_client_info,
                                                      args=(client, query_model, bplan_id, lang))
                Thread_client_experience = threading.Thread(target=get_api_content_client_experience,
                                                            args=(client, query_model, bplan_id, lang))
                Threa_client_partners = threading.Thread(target=get_api_content_client_partners,
                                                         args=(client, query_model, bplan_id, lang))
                Thread_client_expenses = threading.Thread(target=get_api_content_client_expenses,
                                                          args=(client, query_model, bplan_id, lang))
                Thread_client_employed = threading.Thread(target=get_api_content_client_employed,
                                                          args=(client, query_model, bplan_id, lang))
                Thread_client_side_business = threading.Thread(target=get_api_content_client_side_business,
                                                               args=(client, query_model, bplan_id, lang))

                threads = [Thread_client_info, Thread_client_experience, Threa_client_partners, Thread_client_expenses,
                           Thread_client_employed, Thread_client_side_business]
                for thread in threads:
                    thread.start()
                all_threads.extend(threads)

            if request.form.get('flexSwitchCheck_business_profile') is not None:
                Thread_business_profile = threading.Thread(target=get_api_content_business_profile,
                                                           args=(client, query_model, bplan_id, lang))
                Thread_buz_product_services = threading.Thread(target=get_api_content_buz_product_services,
                                                               args=(client, query_model, bplan_id, lang))
                Thread_buz_staff = threading.Thread(target=get_api_content_buz_staff,
                                                    args=(client, query_model, bplan_id, lang))
                Thread_buz_resources = threading.Thread(target=get_api_content_buz_resources,
                                                        args=(client, query_model, bplan_id, lang))
                Thread_source_funding = threading.Thread(target=get_api_content_source_funding,
                                                         args=(client, query_model, bplan_id, lang))
                Thread_financial_history = threading.Thread(target=get_api_content_financial_history,
                                                            args=(client, query_model, bplan_id, lang))

                threads = [Thread_business_profile, Thread_buz_product_services, Thread_buz_staff, Thread_buz_resources,
                           Thread_source_funding, Thread_financial_history]
                for thread in threads:
                    thread.start()
                all_threads.extend(threads)

            if request.form.get('flexSwitchCheck_business_premises') is not None:
                Thread_business_premises = threading.Thread(target=get_api_content_business_premises,
                                                            args=(client, query_model, bplan_id, lang))
                Thread_business_premises.start()
                all_threads.append(Thread_business_premises)

            if request.form.get('flexSwitchCheck_market_analysis') is not None:
                print('calling the function')
                Thread_market_analysis = threading.Thread(target=get_api_content_market_analysis,
                                                          args=(client, query_model, bplan_id, lang))
                Thread_market_analysis.start()
                all_threads.append(Thread_market_analysis)

            if request.form.get('flexSwitchCheck_operations_plan') is not None:
                Thread_buz_suppliers = threading.Thread(target=get_api_content_buz_suppliers,
                                                        args=(client, query_model, bplan_id, lang))
                Thread_buz_production = threading.Thread(target=get_api_content_buz_production,
                                                         args=(client, query_model, bplan_id, lang))
                Thread_buz_distribution = threading.Thread(target=get_api_content_buz_distribution,
                                                           args=(client, query_model, bplan_id, lang))

                threads = [Thread_buz_suppliers, Thread_buz_production, Thread_buz_distribution]
                for thread in threads:
                    thread.start()
                all_threads.extend(threads)

            if request.form.get('flexSwitchCheck_requested_fund') is not None:
                Thread_requested_fund = threading.Thread(target=get_api_content_requested_fund,
                                                         args=(client, query_model, bplan_id, lang))
                Thread_requested_fund.start()
                all_threads.append(Thread_requested_fund)

            if request.form.get('flexSwitchCheck_feasibility') is not None:
                Thread_feasibility = threading.Thread(target=get_api_content_feasibility,
                                                      args=(client, query_model, bplan_id, lang))
                Thread_feasibility.start()
                all_threads.append(Thread_feasibility)

            # Wait for ALL content generation threads to complete
            print(f"DEBUG: Waiting for {len(all_threads)} threads to complete...")
            for thread in all_threads:
                thread.join(timeout=60)  # 60 second timeout per thread
            print("DEBUG: All content generation threads completed")

            # Update checkboxes after all content is generated
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

            # Generate mission/vision and objectives after everything is definitely done
            print("DEBUG: Starting mission/vision and objectives generation...")

            # Start both threads
            Thread_mission_vision = threading.Thread(target=generate_mission_vision_statements,
                                                     args=(client, query_model, bplan_id, lang))
            Thread_objectives = threading.Thread(target=get_api_content_objectives,
                                                 args=(client, query_model, bplan_id, lang))

            # Start both threads
            Thread_mission_vision.start()
            Thread_objectives.start()

            # Wait for both to complete
            Thread_mission_vision.join(timeout=45)  # 45 second timeout for mission/vision
            Thread_objectives.join(timeout=30)  # 30 second timeout for objectives

            print("DEBUG: Mission/vision and objectives generation completed")

            time.sleep(2)  # Final brief pause to ensure all database commits are complete

        return redirect(url_for('home_blueprint.export_plan', bplan_id=bplan_id))

    # Render the page normally for GET and after POST (non-PDF)
    return render_template(
        'home/exportplan.html',
        segment='exportplan',
        data_checkboxes=data_export_plan_checkboxes, # New check Boxes
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
        # NEW: Add projection data for normal rendering
        data_projections=data_projections,
        data_total_projections=data_total_projections,
        current_inflation_rate=inflation_rate,
        data_price=data_price_preferences,
        data_service=data_service_preferences,
        data_quality=data_quality_preferences,
        data_location=data_location_preferences,
        data_comp_preferences=data_comp_preferences,
        data_compname=data_buz_competitor
    )


@blueprint.route('/export_plan/status/<bplan_id>', methods=['GET'])
@login_required
def export_plan_status(bplan_id):
    """Check if AI generation is complete for the requested sections"""
    data_export_plan, status_export_plan = get_export_plan(bplan_id)

    if not data_export_plan:
        return jsonify({'complete': False})

    export_data = data_export_plan[0]
    checks = []

    # Check which sections were requested and verify they have AI-generated content
    if request.args.get('check_client_profile'):
        # For client profile, check multiple fields since it has multiple threads
        client_profile_checks = [
            export_data.client_profile and len(export_data.client_profile.strip()) > 100,
            export_data.client_experiences and len(export_data.client_experiences.strip()) > 50,
            export_data.client_partners and len(export_data.client_partners.strip()) > 50,
            export_data.client_expenses and len(export_data.client_expenses.strip()) > 50,
            export_data.client_employed and len(export_data.client_employed.strip()) > 50
        ]
        # Require majority of client profile fields to be populated
        checks.append(sum(client_profile_checks) >= 3)

    if request.args.get('check_business_profile'):
        # For business profile, check multiple fields
        business_profile_checks = [
            export_data.business_profile and len(export_data.business_profile.strip()) > 100,
            export_data.buz_staff and len(export_data.buz_staff.strip()) > 50,
            export_data.buz_resource and len(export_data.buz_resource.strip()) > 50,
            export_data.financial_history and len(export_data.financial_history.strip()) > 50,
            export_data.source_of_funding and len(export_data.source_of_funding.strip()) > 50
        ]
        # Require majority of business profile fields to be populated
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
        # For operations plan, check all three fields
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

    # If we have checks to perform, all must be complete
    # If no specific checks (shouldn't happen), return False
    is_complete = bool(checks) and all(checks)

    return jsonify({
        'complete': is_complete,
        'checks_performed': len(checks),
        'checks_passed': sum(checks)
    })


