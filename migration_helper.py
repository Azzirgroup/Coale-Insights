#!/usr/bin/env python3
"""
Insights API Migration Helper
Helps migrate from deprecated insights.api.ml to modular insights.api.ml structure

Usage:
    python migration_helper.py --check-imports
    python migration_helper.py --migrate-file <file_path>
    python migration_helper.py --scan-project <project_path>
"""

import os
import re
import argparse
from typing import List, Dict, Set
from pathlib import Path


class InsightsAPIMigrator:
    """Helper class for migrating Insights API imports"""

    # Mapping of old monolithic functions to new modular locations
    FUNCTION_MAPPING = {
        # Customer functions
        'customer_segmentation': 'insights.api.ml.customer',
        'get_segment_summary': 'insights.api.ml.customer',
        'customer_intelligence': 'insights.api.ml.customer',
        'customer_intelligence_status': 'insights.api.ml.customer',
        'customer_360': 'insights.api.ml.customer',
        'customer_360_detail': 'insights.api.ml.customer',
        'purchase_patterns': 'insights.api.ml.customer',
        'cross_sell_opportunities': 'insights.api.ml.customer',
        'at_risk_customers': 'insights.api.ml.customer',
        'geographic_insights': 'insights.api.ml.customer',
        'next_best_actions': 'insights.api.ml.customer',
        'pareto_analysis': 'insights.api.ml.customer',
        'cohort_retention': 'insights.api.ml.customer',
        'refresh_customer_scores': 'insights.api.ml.customer',

        # Sales functions
        'sales_forecast': 'insights.api.ml.sales',
        'get_forecast_chart_data': 'insights.api.ml.sales',
        'sales_intelligence': 'insights.api.ml.sales',
        'payment_mix': 'insights.api.ml.sales',
        'sales_rep_performance': 'insights.api.ml.sales',
        'revenue_breakdown': 'insights.api.ml.sales',
        'margin_analysis': 'insights.api.ml.sales',
        'sales_comparisons': 'insights.api.ml.sales',
        'train_forecast_models': 'insights.api.ml.sales',
        'get_historical_and_forecast_by_dimension': 'insights.api.ml.sales',

        # Inventory functions
        'inventory_classification': 'insights.api.ml.inventory',
        'get_inventory_recommendations': 'insights.api.ml.inventory',
        'inventory_intelligence': 'insights.api.ml.inventory',
        'train_inventory_intelligence': 'insights.api.ml.inventory',
        'get_stock_overview': 'insights.api.ml.inventory',
        'get_turnover_analysis': 'insights.api.ml.inventory',
        'get_aging_analysis': 'insights.api.ml.inventory',
        'get_warehouse_analysis': 'insights.api.ml.inventory',
        'get_transfer_recommendations': 'insights.api.ml.inventory',
        'get_dead_stock': 'insights.api.ml.inventory',

        # Procurement functions
        'get_procurement_insights': 'insights.api.ml.procurement',
        'procurement_intelligence': 'insights.api.ml.procurement',
        'train_procurement_intelligence': 'insights.api.ml.procurement',
        'get_spend_overview': 'insights.api.ml.procurement',
        'get_supplier_performance': 'insights.api.ml.procurement',
        'get_purchase_analytics': 'insights.api.ml.procurement',
        'get_price_intelligence': 'insights.api.ml.procurement',
        'get_procurement_risks': 'insights.api.ml.procurement',
        'get_procurement_forecast': 'insights.api.ml.procurement',

        # Financial functions
        'financial_intelligence': 'insights.api.ml.financial',
        'train_financial_intelligence': 'insights.api.ml.financial',
        'get_financial_overview': 'insights.api.ml.financial',
        'get_cash_flow_analysis': 'insights.api.ml.financial',
        'get_receivables_analysis': 'insights.api.ml.financial',
        'get_payables_analysis': 'insights.api.ml.financial',
        'get_budget_analysis': 'insights.api.ml.financial',
        'get_financial_ratios': 'insights.api.ml.financial',
        'get_kra_tax_analysis': 'insights.api.ml.financial',
        'get_forex_exposure': 'insights.api.ml.financial',
        'get_financial_forecasts': 'insights.api.ml.financial',

        # HR functions
        'get_hr_overview': 'insights.api.ml.hr',
        'get_headcount_analytics': 'insights.api.ml.hr',
        'get_attrition_analytics': 'insights.api.ml.hr',
        'get_payroll_analytics': 'insights.api.ml.hr',
        'get_workforce_planning': 'insights.api.ml.hr',
        'get_hr_insights': 'insights.api.ml.hr',
        'get_talent_analytics': 'insights.api.ml.hr',
        'analyze_hr_query': 'insights.api.ml.hr',

        # Executive functions
        'get_executive_summary': 'insights.api.ml.executive',
        'get_business_health_score': 'insights.api.ml.executive',
        'get_executive_kpis': 'insights.api.ml.executive',
        'get_executive_alerts': 'insights.api.ml.executive',
        'get_executive_trends': 'insights.api.ml.executive',
        'get_executive_insights': 'insights.api.ml.executive',
        'get_department_insights': 'insights.api.ml.executive',
        'get_strategic_recommendations': 'insights.api.ml.executive',
        'analyze_executive_query': 'insights.api.ml.executive',
        'generate_executive_report': 'insights.api.ml.executive',
        'send_executive_report': 'insights.api.ml.executive',
        'get_executive_reports_status': 'insights.api.ml.executive',
        'get_recent_executive_reports': 'insights.api.ml.executive',
        'download_executive_report': 'insights.api.ml.executive',
        'test_executive_intelligence_data': 'insights.api.ml.executive',
        'preview_executive_report_data': 'insights.api.ml.executive',

        # Search functions
        'perform_cross_dashboard_search': 'insights.api.ml.search',
        'get_search_suggestions': 'insights.api.ml.search',
        'get_search_history': 'insights.api.ml.search',
        'save_search_favorite': 'insights.api.ml.search',
        'get_cross_dashboard_navigation': 'insights.api.ml.search',
        'get_search_help': 'insights.api.ml.search',
        'search_domain_data': 'insights.api.ml.search',
        'get_available_search_filters': 'insights.api.ml.search',

        # Predictive functions
        'generate_comprehensive_forecasts': 'insights.api.ml.predictive',
        'detect_anomalies_and_risks': 'insights.api.ml.predictive',
        'analyze_predictive_patterns': 'insights.api.ml.predictive',
        'get_real_time_predictions': 'insights.api.ml.predictive',
        'optimize_prediction_models': 'insights.api.ml.predictive',
        'get_predictive_insights': 'insights.api.ml.predictive',
        'get_risk_assessment': 'insights.api.ml.predictive',
        'get_domain_comparison': 'insights.api.ml.predictive',

        # General functions
        'get_ml_status': 'insights.api.ml.general',
        'run_all_models': 'insights.api.ml.general',
        'payment_risk_analysis': 'insights.api.ml.general',
        'get_high_risk_invoices': 'insights.api.ml.general',
        'demand_forecast': 'insights.api.ml.general',
        'get_reorder_alerts': 'insights.api.ml.general',
        'product_recommendations': 'insights.api.ml.general',
        'recommend_for_item': 'insights.api.ml.general',
        'recommend_for_customer': 'insights.api.ml.general',
        'recommend_for_cart': 'insights.api.ml.general',
        'get_dashboard_data': 'insights.api.ml.general',
        'get_ml_insights_summary': 'insights.api.ml.general',
    }

    def __init__(self):
        self.files_checked = 0
        self.files_with_imports = 0
        self.migrations_needed = 0

    def scan_file(self, file_path: str) -> Dict[str, List[str]]:
        """Scan a file for deprecated Insights API imports"""
        results = {
            'deprecated_imports': [],
            'functions_to_migrate': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for deprecated import patterns
            import_patterns = [
                r'from insights\.api\.ml import',
                r'import insights\.api\.ml',
                r'from insights\.api import ml',
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    results['deprecated_imports'].extend(matches)

            # Check for function usage from deprecated module
            for func_name in self.FUNCTION_MAPPING.keys():
                if re.search(rf'\b{func_name}\s*\(', content):
                    results['functions_to_migrate'].append(func_name)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

        return results

    def migrate_file(self, file_path: str, dry_run: bool = True) -> bool:
        """Migrate a file from old to new API imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Replace import statements
            content = re.sub(
                r'from insights\.api\.ml import (.+)',
                r'# DEPRECATED: from insights.api.ml import \1\n# Migrate to domain-specific imports',
                content
            )

            content = re.sub(
                r'import insights\.api\.ml',
                r'# DEPRECATED: import insights.api.ml\n# Migrate to domain-specific imports',
                content
            )

            # Add migration guidance comment at top if changes were made
            if content != original_content:
                migration_comment = f'''"""
MIGRATION REQUIRED: {os.path.basename(file_path)}

This file contains deprecated imports from insights.api.ml
Please update to use domain-specific modules:

from insights.api.ml.customer import customer_segmentation
from insights.api.ml.sales import sales_forecast
# etc.

See DEPRECATION_NOTICE.md for full migration guide.
"""
'''
                content = migration_comment + content

            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                print(f"Would migrate {file_path}")
                return True

        except Exception as e:
            print(f"Error migrating {file_path}: {e}")
            return False

    def scan_project(self, project_path: str) -> Dict[str, List]:
        """Scan entire project for deprecated API usage"""
        results = {
            'files_with_deprecated_imports': [],
            'files_with_functions_to_migrate': [],
            'summary': {}
        }

        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.vscode'}]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        for file_path in python_files:
            self.files_checked += 1
            scan_result = self.scan_file(file_path)

            if scan_result['deprecated_imports']:
                self.files_with_imports += 1
                results['files_with_deprecated_imports'].append({
                    'file': file_path,
                    'imports': scan_result['deprecated_imports']
                })

            if scan_result['functions_to_migrate']:
                self.migrations_needed += 1
                results['files_with_functions_to_migrate'].append({
                    'file': file_path,
                    'functions': scan_result['functions_to_migrate']
                })

        results['summary'] = {
            'total_files_scanned': self.files_checked,
            'files_with_deprecated_imports': self.files_with_imports,
            'files_needing_migration': self.migrations_needed
        }

        return results


def main():
    parser = argparse.ArgumentParser(description='Insights API Migration Helper')
    parser.add_argument('--check-imports', action='store_true',
                       help='Check for deprecated imports in the current directory')
    parser.add_argument('--migrate-file', type=str,
                       help='Migrate a specific file')
    parser.add_argument('--scan-project', type=str,
                       help='Scan entire project directory')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without making changes')

    args = parser.parse_args()

    migrator = InsightsAPIMigrator()

    if args.check_imports:
        results = migrator.scan_project('.')
        print("=== Insights API Migration Scan Results ===")
        print(f"Files scanned: {results['summary']['total_files_scanned']}")
        print(f"Files with deprecated imports: {results['summary']['files_with_deprecated_imports']}")
        print(f"Files needing migration: {results['summary']['files_needing_migration']}")

        if results['files_with_deprecated_imports']:
            print("\nFiles with deprecated imports:")
            for item in results['files_with_deprecated_imports']:
                print(f"  {item['file']}")
                for imp in item['imports']:
                    print(f"    - {imp}")

    elif args.migrate_file:
        success = migrator.migrate_file(args.migrate_file, args.dry_run)
        if success:
            print(f"Successfully migrated {args.migrate_file}")
        else:
            print(f"Failed to migrate {args.migrate_file}")

    elif args.scan_project:
        results = migrator.scan_project(args.scan_project)
        print(f"Scanned {results['summary']['total_files_scanned']} files")
        print(f"Found {results['summary']['files_with_deprecated_imports']} files with deprecated imports")
        print(f"Found {results['summary']['files_needing_migration']} files needing migration")


if __name__ == '__main__':
    main()