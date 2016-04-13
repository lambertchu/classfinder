from django.test import TestCase
from generate_recs import calculate_rating
import get_new_classes

class GenerateRecsTestCase(TestCase):
	def setUp(self):
		pass

	# def test_create_totals_table(self):
	# 	all_classes = ['6.01', '6.02', '18.06']
	# 	class_table = {'6.01':0, '6.02':1, '18.06':2}
	# 	shared_classes_table = [[2,1,2],[1,2,2],[2,2,3]]

	# 	DICT = {'6.01':2, '6.02':2, '18.06':3}
	#   self.assertEqual(generate_recs.create_totals_table(all_classes, class_table, shared_classes_table), DICT)

	def test_create_shared_classes_table(self):
		pass

	def test_calculate_rating(self):

		"""
		Helper function for comparing float values
		"""
		def isclose(a, b, rel_tol=1e-04, abs_tol=0.0):
			return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

		student_classes_list = ['6.01', '6.02', '18.06']
		class_table = {'6.01':0, '6.02':1, '18.06':2, '6.042':3, '6.004':4, '6.005':5}
		shared_classes_table = [[5,1,2,4,4,3],[1,5,2,3,4,2],[2,2,6,1,2,1],[4,3,1,4,3,3],[4,4,2,3,5,2],[3,2,1,3,2,4]]

		rating1 = calculate_rating('6.042', student_classes_list, class_table, shared_classes_table)
		rating2 = calculate_rating('6.004', student_classes_list, class_table, shared_classes_table)
		rating3 = calculate_rating('6.005', student_classes_list, class_table, shared_classes_table)

		comp1 = isclose(rating1, 2.18876)
		comp2 = isclose(rating2, 2.62917)
		comp3 = isclose(rating3, 1.792)

		self.assertTrue(comp1)
		self.assertTrue(comp2)
		self.assertTrue(comp3)



class GetClassesToTakeTestCase(TestCase):
	def setUp(self):
		pass

	def test_get_classes_to_take_1(self):
		taken = ['6.01', '6.042', '6.UAR']
		reqs = ['6.01', [1, '6.UAR', [2, '6.UAT', '6.UAP']]]
		new_classes = get_new_classes.get_classes_to_take(None, taken, reqs)

		self.assertEqual(new_classes, [])


	def test_get_classes_to_take_2(self):
		taken = ['6.01', '6.042']
		reqs = ['6.01', [1, '6.UAR', [2, '6.UAT', '6.UAP']]]
		new_classes = get_new_classes.get_classes_to_take(None, taken, reqs)

		self.assertTrue('6.UAR' in new_classes)
		self.assertTrue('6.UAT' in new_classes)
		self.assertTrue('6.UAP' in new_classes)
		self.assertTrue('6.01' not in new_classes)


	def test_get_classes_to_take_3(self):
		taken = ['6.046', '6.01', '6.042']
		reqs = [[3, "6.033", [1, "6.034", "6.036"], [1, "6.045", "6.046"]]]
		new_classes = get_new_classes.get_classes_to_take(None, taken, reqs)

		self.assertTrue('6.033' in new_classes)
		self.assertTrue('6.034' in new_classes)
		self.assertTrue('6.036' in new_classes)
		self.assertTrue('6.045' not in new_classes)
		self.assertTrue('6.046' not in new_classes)


	def test_get_classes_to_take_double_nested_1(self):
		taken = ['2.02A', '1.00', '6.000', '99.99']
		reqs = [[1, [2, "2.001", [1, "2.02A", "2.002"]], [2, "2.01", [1, "2.02A", "2.02B", "2.002"]]]]

		new_classes = get_new_classes.get_classes_to_take(None, taken, reqs)

		self.assertTrue('2.001' in new_classes)
		self.assertTrue('2.01' in new_classes)
		self.assertTrue('2.02A' not in new_classes)
		self.assertTrue('2.002' not in new_classes)
		self.assertTrue('2.02B' not in new_classes)


	def test_get_classes_to_take_double_nested_2(self):
		taken = ['2.01', '1.00', '6.000', '99.99']
		reqs = [[1, [2, "2.001", [1, "2.02A", "2.002"]], [2, "2.01", [1, "2.02A", "2.02B", "2.002"]]]]

		new_classes = get_new_classes.get_classes_to_take(None, taken, reqs)

		self.assertTrue('2.001' in new_classes)
		self.assertTrue('2.002' in new_classes)
		self.assertTrue('2.02A' in new_classes)
		self.assertTrue('2.02B' in new_classes)
		self.assertTrue('2.01' not in new_classes)


	def test_get_classes_to_take_double_nested_3(self):
		taken = ['2.001', '2.02A', '6.000', '99.99']
		reqs = [[2, [2, "2.001", [1, "2.02A", "2.002"]], [2, "2.01", [1, "2.02A", "2.02B", "2.002"]]]]

		new_classes = get_new_classes.get_classes_to_take(None, taken, reqs)

		self.assertTrue('2.001' not in new_classes)
		self.assertTrue('2.002' not in new_classes)
		self.assertTrue('2.02A' not in new_classes)
		self.assertTrue('2.02B' not in new_classes)
		self.assertTrue('2.01' in new_classes)

