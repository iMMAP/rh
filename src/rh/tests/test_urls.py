# from django.test import SimpleTestCase
# from django.urls import resolve, reverse

# from rh.views import (
#     active_projects_view,
#     archive_project,
#     archived_projects_view,
#     completed_projects_view,
#     copy_activity_plan,
#     copy_project,
#     copy_target_location,
#     create_project_budget_progress_view,
#     create_project_view,
#     delete_activity_plan,
#     delete_budget_progress,
#     delete_project,
#     delete_target_location,
#     draft_projects_view,
#     home,
#     index,
#     load_facility_sites,
#     load_locations_details,
#     open_project_view,
#     project_planning_review,
#     submit_project,
#     unarchive_project,
#     update_project_view,
# )


# class TestUrls(SimpleTestCase):
#     def test_index_url_resolves(self):
#         url = reverse("index")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, index)
#         print("Test for index URL resolved successfully.")

#     def test_home_url_resolves(self):
#         url = reverse("home")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, home)
#         print("Test for home URL resolved successfully.")

#     # Test Project URLS

#     def test_draft_projects_url_resolves(self):
#         url = reverse("draft_projects")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, draft_projects_view)
#         print("Test for draft_projects URL resolved successfully.")

#     def test_active_projects_url_resolves(self):
#         url = reverse("active_projects")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, active_projects_view)
#         print("Test for active_projects URL resolved successfully.")

#     def test_completed_projects_url_resolves(self):
#         url = reverse("completed_projects")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, completed_projects_view)
#         print("Test for completed_projects URL resolved successfully.")

#     def test_archived_projects_url_resolves(self):
#         url = reverse("archived_projects")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, archived_projects_view)
#         print("Test for archived_projects URL resolved successfully.")

#     def test_create_project_url_resolves(self):
#         url = reverse("create_project")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, create_project_view)
#         print("Test for create_project URL resolved successfully.")

#     def test_update_project_url_resolves(self):
#         url = reverse("update_project", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, update_project_view)
#         print("Test for update_project URL resolved successfully.")

#     def test_archive_project_url_resolves(self):
#         url = reverse("archive_project", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, archive_project)
#         print("Test for archive_project URL resolved successfully.")

#     def test_unarchive_project_url_resolves(self):
#         url = reverse("unarchive_project", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, unarchive_project)
#         print("Test for unarchive_project URL resolved successfully.")

#     def test_delete_project_url_resolves(self):
#         url = reverse("delete_project", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, delete_project)
#         print("Test for delete_project URL resolved successfully.")

#     def test_copy_project_url_resolves(self):
#         url = reverse("copy_project", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, copy_project)
#         print("Test for copy_project URL resolved successfully.")

#     def test_open_project_view_url_resolves(self):
#         url = reverse("view_project", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, open_project_view)
#         print("Test for view_project URL resolved successfully.")

#     # Project Activity Planning Tests

#     def test_copy_activity_plan_url_resolves(self):
#         url = reverse("copy_plan", args=["1", "2"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, copy_activity_plan)
#         print("Test for copy_plan URL resolved successfully.")

#     def test_delete_activity_plan_url_resolves(self):
#         url = reverse("delete_plan", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, delete_activity_plan)
#         print("Test for delete_plan URL resolved successfully.")

#     def test_copy_target_location_url_resolves(self):
#         url = reverse("copy_location", args=["1", "2"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, copy_target_location)
#         print("Test for copy_location URL resolved successfully.")

#     def test_delete_target_location_url_resolves(self):
#         url = reverse("delete_location", args=["1"])
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, delete_target_location)
#         print("Test for delete_location URL resolved successfully.")

#     # FIXME: Create a dummy project with id 1
#     def test_create_project_budget_progress_view_url_resolves(self):
#         self.skipTest("Will adjust this later")
#         # Create a dummy project with id 1
#         url = reverse(
#             "create_project_budget_progress", kwargs={"project": "1"}
#         )  # Replace '1' with an actual project ID
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, create_project_budget_progress_view)
#         print("Test for create_project_budget_progress_view URL resolved successfully.")

#     def test_delete_budget_progress_url_resolves(self):
#         url = reverse("delete_budget", kwargs={"pk": "1"})  # Replace '1' with an actual budget ID
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, delete_budget_progress)
#         print("Test for delete_budget_progress URL resolved successfully.")

#     # FIXME: FIX this - Create a dummy project first
#     def test_project_planning_review_url_resolves(self):
#         self.skipTest("Will Fix Later")
#         url = reverse("project_plan_review", kwargs={"project": "1"})  # Replace '1' with an actual project ID
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, project_planning_review)
#         print("Test for project_planning_review URL resolved successfully.")

#     def test_submit_project_url_resolves(self):
#         url = reverse("project_submit", kwargs={"pk": "1"})  # Replace '1' with an actual project ID
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, submit_project)
#         print("Test for submit_project URL resolved successfully.")

#     def test_load_locations_details_url_resolves(self):
#         url = reverse("ajax-load-locations")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, load_locations_details)
#         print("Test for load_locations_details URL resolved successfully.")

#     def test_load_facility_sites_url_resolves(self):
#         url = reverse("ajax-load-facility_sites")
#         resolver = resolve(url)
#         self.assertEqual(resolver.func, load_facility_sites)
#         print("Test for load_facility_sites URL resolved successfully.")
