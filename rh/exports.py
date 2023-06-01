from django.http import JsonResponse

from django.views import View
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, NamedStyle
from io import BytesIO
import base64
from django.utils import timezone

from .filters import *
from .forms import *


#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name='header')
header_style.font = Font(bold=True)


class ProjectExportExcelView(View):
    """
    View class for exporting project data to Excel.
    """

    def post(self, request):
        """
        Handle POST request to export project data to Excel.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: The JSON response containing the file URL and name, or an error message.
        """
        try:
            selected_ids = [int(i) for i in request.POST.getlist('selected_ids') if i]  # Get the selected record IDs
            queryset = Project.objects.filter(id__in=selected_ids)  # Filter the queryset based on selected IDs

            workbook = Workbook()

            self.write_project_sheet(workbook, queryset)
            self.write_population_sheet(workbook, queryset)
            self.write_target_locations_sheet(workbook, queryset)

            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            response = {
                'file_url': 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + base64.b64encode(excel_file.read()).decode('utf-8'),
                'file_name': 'export.xlsx',
            }

            return JsonResponse(response)
        except Exception as e:
            response = {'error': str(e)}
            return JsonResponse(response, status=500)

    def write_project_sheet(self, workbook, queryset):
        """
        Write the project sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            queryset (QuerySet): The queryset containing the project data.
        """
        sheet = workbook.active
        sheet.title = 'Project'

        # Define column headers and types
        columns = [
            {'header': 'Focal Person', 'type': 'string', 'width': 20},
            {'header': 'Email', 'type': 'string', 'width': 25},
            # ... Define other columns ...
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_project_data_rows(sheet, queryset)

    def write_sheet_columns(self, sheet, columns):
        """
        Write column headers and formatting for a sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            columns (list): List of dictionaries containing column header, type, and width information.
        """
        for idx, column in enumerate(columns, start=1):
            cell = sheet.cell(row=1, column=idx, value=column['header'])
            cell.style = header_style

            column_letter = get_column_letter(idx)
            if column['type'] == 'number':
                sheet.column_dimensions[column_letter].number_format = 'General'
            elif column['type'] == 'date':
                sheet.column_dimensions[column_letter].number_format = 'mm-dd-yyyy'

            sheet.column_dimensions[column_letter].width = column['width']

    def write_project_data_rows(self, sheet, queryset):
        """
        Write project data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            queryset (QuerySet): The queryset containing the project data.
        """
        for row_idx, project in enumerate(queryset, start=2):
            row = [
                project.user.profile.name,
                project.user.email,
                project.title,
                project.code,
                project.description,
                project.hrp_code,
                project.start_date.astimezone(timezone.utc).replace(tzinfo=None) if project.start_date else None,
                project.end_date.astimezone(timezone.utc).replace(tzinfo=None) if project.end_date else None,
                project.budget,
                project.budget_received,
                project.budget_gap,
                project.budget_currency.name,
                ', '.join([donor.name for donor in project.donors.all()]),
                ', '.join([implementing_partner.name for implementing_partner in project.implementing_partners.all()]),
                ', '.join([programme_partner.name for programme_partner in project.programme_partners.all()]),
                project.state,
                'URL',
            ]

            for col_idx, value in enumerate(row, start=1):
                cell = sheet.cell(row=row_idx, column=col_idx, value=value)

        sheet.freeze_panes = sheet['A2']

    def write_population_sheet(self, workbook, queryset):
        """
        Write the population sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            queryset (QuerySet): The queryset containing the project data.
        """
        sheet = workbook.create_sheet(title='Population')

        # Define column headers and types for Sheet 2
        columns = [
            {'header': 'Activity Domain', 'type': 'string', 'width': 20},
            {'header': 'Activity Type', 'type': 'string', 'width': 20},
            {'header': 'Activity Detail', 'type': 'string', 'width': 20},
            {'header': 'Indicators', 'type': 'string', 'width': 40},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_population_data_rows(sheet, queryset)

        sheet.freeze_panes = sheet['A2']

    def write_population_data_rows(self, sheet, queryset):
        """
        Write population data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            queryset (QuerySet): The queryset containing the project data.
        """
        for row_idx, project in enumerate(queryset, start=2):
            activity_plans = project.activityplan_set.all()
            for plan in activity_plans:
                row = [
                    plan.activity_domain.name,
                    plan.activity_type.name,
                    plan.activity_detail.name if plan.activity_detail else None,
                    '\n'.join([indicator.name for indicator in plan.indicators.all()]),
                ]

                for col_idx, value in enumerate(row, start=1):
                    cell = sheet.cell(row=row_idx, column=col_idx, value=value)

    def write_target_locations_sheet(self, workbook, queryset):
        """
        Write the target locations sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            queryset (QuerySet): The queryset containing the project data.
        """
        sheet = workbook.create_sheet(title='Target Locations')

        # Define column headers and types for Sheet 3
        columns = [
            {'header': 'Province', 'type': 'string', 'width': 20},
            {'header': 'District', 'type': 'string', 'width': 20},
            {'header': 'Zone/Ward', 'type': 'string', 'width': 20},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_target_locations_data_rows(sheet, queryset)

        sheet.freeze_panes = sheet['A2']

    def write_target_locations_data_rows(self, sheet, queryset):
        """
        Write target locations data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            queryset (QuerySet): The queryset containing the project data.
        """
        for row_idx, project in enumerate(queryset, start=2):
            target_locations = project.targetlocation_set.all()
            for location in target_locations:
                row = [
                    location.province.name,
                    location.district.name,
                    location.zone.name if location.zone else None,
                ]

                for col_idx, value in enumerate(row, start=1):
                    cell = sheet.cell(row=row_idx, column=col_idx, value=value)
