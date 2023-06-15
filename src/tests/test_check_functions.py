import pandas as pd

from validator.check_functions import (conditional_field_conflict,
                                       denial_reasons_conditional_enum_value,
                                       duplicates_in_field,
                                       enum_value_conflict,
                                       invalid_date_format, invalid_enum_value,
                                       invalid_number_of_values, is_number,
                                       multi_invalid_number_of_values,
                                       multi_value_field_restriction)


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    invalid_date_format_1 = "202310101"
    invalid_date_format_2 = "20231032"
    invalid_date_format_3 = "20231301"
    invalid_date_format_4 = "00001201"
    
    def test_with_valid_date(self):
        assert invalid_date_format(self.valid_date_format) == True
        
    def test_with_invalid_date(self):
        assert invalid_date_format(self.invalid_date_format_1) == False
        
    def test_with_invalid_day(self):
        assert invalid_date_format(self.invalid_date_format_2) == False
        
    def test_with_invalid_month(self):
        assert invalid_date_format(self.invalid_date_format_3) == False
        
    def test_with_invalid_year(self):
        assert invalid_date_format(self.invalid_date_format_4) == False


class TestDenialReasonsConditionalEnumValue:
    def test_with_correct_action_taken_and_denial_reasons(self):
        
        #if action taken != 3 then denial_reasons must be 999
        series =  pd.Series(['999'],
                    name="denial_reasons",
                    index=[2]
                )
        result = denial_reasons_conditional_enum_value({"4":series})
        assert result.values == [True]
        
        #if action taken = 3 then denial_reasons must not contains 999
        series_2 =  pd.Series(['997'],
                    name="denial_reasons",
                    index=[2]
                )
        result_2 = denial_reasons_conditional_enum_value({"3":series_2})
        assert result_2.values == [True]
        
        #if action taken = 3 then denial_reasons must not contains 999 and
        # can have multiple values
        series_3 =  pd.Series(['997;1'],
                    name="denial_reasons",
                    index=[2]
                )
        result_3 = denial_reasons_conditional_enum_value({"3":series_3})
        assert result_3.values == [True]
       
    def test_with_incorrect_action_taken_and_denial_reasons(self):
        
        #if action taken != 3 and denial_reasons is not 999 
        #  , it should fail
        series =  pd.Series(['997'],
                    name="denial_reasons",
                    index=[2]
                )
        result = denial_reasons_conditional_enum_value({"4":series})
        assert result.values == [False]
        
        #if action taken = 3 and denial_reasons is 999
        #  , it should fail
        series_2 =  pd.Series(['999'],
                    name="denial_reasons",
                    index=[2]
                )
        result_2 = denial_reasons_conditional_enum_value({"3":series_2})
        assert result_2.values == [False]
        
         #if action taken = 3 and denial_reasons is 999
        #  , it should fail
        series_3 =  pd.Series(['997;999'],
                    name="denial_reasons",
                    index=[2]
                )
        result_3 = denial_reasons_conditional_enum_value({"3":series_3})
        assert result_3.values == [False]
        
        #if action taken = 3 then denial_reasons 
        # can have multiple values but can not contains 999 
        series_4 =  pd.Series(['997;1;999'],
                    name="denial_reasons",
                    index=[2]
                )
        result_4 = denial_reasons_conditional_enum_value({"3":series_4})
        assert result_4.values == [False]

class TestDuplicatesInField:
    
    def test_with_blank(self):
        assert duplicates_in_field("") == True
        
    def test_with_no_duplicates(self):
        assert duplicates_in_field("1") == True
        assert duplicates_in_field("1;2;3;4") == True
        
    def test_with_duplicates(self):
        assert duplicates_in_field("1;2;3;3;4") == False
        

class TestInvalidNumberOfValues:
    
    def test_with_in_range(self):
        assert invalid_number_of_values("1;2;", 1, 4) == True
        
    def test_with_lower_range_value(self):
        assert invalid_number_of_values("1", 1, 4) == True
        
    def test_with_invalid_lower_range_value(self):
        assert invalid_number_of_values("1", 2, 4) == False
        
    def test_with_upper_range_value(self):
        assert invalid_number_of_values("1;2", 1, 2) == True
        
    def test_with_invalid_upper_range_value(self):
        assert invalid_number_of_values("1;2;3;4", 2, 3) == False
        

class TestMultiValueFieldRestriction:
    
    def test_with_invalid_values(self):
        assert multi_value_field_restriction("1;2;3", ["2"] ) == False
        
    def test_with_valid_length(self):
        assert multi_value_field_restriction("2", ["2"] ) == True
        assert multi_value_field_restriction("1", ["2"] ) == True
        
    def test_with_valid_values(self):
        assert multi_value_field_restriction("1;2;3", ["4"] ) == True
        
        
class TestMultiInvalidNumberOfValues:
    series =  pd.Series(['999'],
                    name="test_name",
                    index=[2]
                )
    
    def test_inside_maxlength(self):
        result = multi_invalid_number_of_values({"4": self.series}, 5)
        assert result.values == [True]
        
    def test_on_maxlength(self):
        result = multi_invalid_number_of_values({"4": self.series}, 2)
        assert result.values == [True]
        
    def test_outside_maxlength(self):
        result = multi_invalid_number_of_values({"4": self.series}, 1)
        assert result.values == [False]

class TestInvalidEnumValue:
    def test_with_valid_enum_values(self):
        accepted_values = ["1","2"]
        result = invalid_enum_value("1;2", accepted_values)
        assert result == True
        
    def test_with_invalid_enum_values(self):
        accepted_values = ["1","2"]
        result = invalid_enum_value("0;3", accepted_values)
        assert result == False
        
class TestIsNumber:
    def test_number_value(self):
        value = "1"
        result = is_number(value)
        assert result == True
        
    def test_non_number_value(self):
        value = "a"
        result = is_number(value)
        assert result == False

class TestConditionalFieldConflict:
    
    def test_conditional_field_conflict_correct(self):
                         
        # if ct_loan_term_flag != 900 then ct_loan_term must be blank
        series =  pd.Series([''],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values: set[str] = { "900" }
        
        result1 = conditional_field_conflict({"988":series}, condition_values)
        print(result1)
        assert result1.values == [True]
        
        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        series2 =  pd.Series(['36'],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values2: set[str] = { "900" }
        result2 = conditional_field_conflict({"900":series2}, condition_values2)
        print(result2)
        assert result2.values == [True]
        
    def test_conditional_field_conflict_incorrect(self):
                         
        # if ct_loan_term_flag != 900 then ct_loan_term must be blank
        # in this test, ct_loan_term_flag is not 900 and ct_loan_term is NOT blank, so must return False
        series =  pd.Series(['36'],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values: set[str] = { "900" }
        
        result1 = conditional_field_conflict({"988":series}, condition_values)
        assert result1.values == [False]
        
        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        # in this testm ct_loan_term is blank, so must return False
        series2 =  pd.Series([''],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values2: set[str] = { "900" }
        result2 = conditional_field_conflict({"900":series2}, condition_values2)
        assert result2.values == [False]
        
class TestEnumValueConflict:
    
    def test_enum_value_confict_correct(self):
        
        # if ct_credit_product = 1 or 2, if ct_loan_term_flag != 999, then return True
        series =  pd.Series(["988"],
                    name="ct_loan_term_flag",
                    index=[2]
        )
        condition_values1: set[str] = { "1", "2" }
        condition_values2 = None
        condition_value = "999"
        ct_credit_product = "1;2"
        result1 = enum_value_conflict({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [True]
        
        # if ct_credit_product = 988 , if ct_loan_term_flag == 999, then return True
        series =  pd.Series(["999"],
                    name="ct_loan_term",
                    index=[2]
        )
        condition_values1 = None
        condition_values2: set[str] = { "988" }
        condition_value = "999"
        ct_credit_product = "988"
        result1 = enum_value_conflict({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [True]
    
    def test_enum_value_confict_incorrect(self):
        
        # if ct_credit_product = 1 or 2, if ct_loan_term_flag == 999, then return False
        series =  pd.Series(["999"],
                    name="ct_loan_term_flag",
                    index=[2]
        )
        condition_values1: set[str] = { "1", "2" }
        condition_values2 = None
        condition_value = "999"
        ct_credit_product = "1;2"
        result1 = enum_value_conflict({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [False]
        
        # if ct_credit_product = 988 , if ct_loan_term_flag != 999, then return False
        series =  pd.Series(["988"],
                    name="ct_loan_term",
                    index=[2]
        )
        condition_values1 = None
        condition_values2: set[str] = { "988" }
        condition_value = "999"
        ct_credit_product = "988"
        result1 = enum_value_conflict({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [False]   
    
