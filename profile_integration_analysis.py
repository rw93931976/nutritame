import requests
import json

def analyze_ai_response_for_profile_integration():
    """Analyze the AI responses from the test to check for profile integration"""
    
    # The AI responses from the test
    first_response = """Absolutely! Let's create a simple, enjoyable meal plan that aligns with your needs for blood sugar control and weight loss. Here's a quick overview of foods you should include and those to keep in mind to limit or avoid.

Foods to Include:
1. Lean proteins:
   - Chicken breast
   - Turkey
   - Fish (like salmon or cod)
   - Eggs
   - Legumes (like lentils and beans)

2. Non-starchy vegetables:
   - Spinach
   - Kale
   - Zucchini
   - Bell peppers
   - Tomatoes 
   - Cucumbers
  
3. Whole grains (in moderation):
   - Quinoa
   - Brown rice
   - Barley

4. Healthy fats: 
   - Olive oil
   - Avocado
   - Seeds (like pumpkin or chia)

5. Low-sugar fruits (in moderation):
   - Berries (strawberries, blueberries)
   - Apples
   - Kiwi

6. Dairy (if you enjoy):
   - Greek yogurt (plain)
   - Low-fat cheese

Foods to Limit or Avoid:
1. Refined carbohydrates:
   - White bread
   - Pastries
   - Sugary cereals

2. Sugary drinks:
   - Soda
   - Fruit juices (especially those with added sugar)

3. High-sugar snacks and desserts:
   - Ice cream
   - Cakes
   - Cookies

4. Processed and fried foods:
   - Fast food
   - Chips

5. High-fat meats:
   - Sausages
   - Bacon

This framework will help you craft meals that are balanced without feeling restrictive. 

Now, would you like me to help you create a specific meal plan for a few days using these guidelines? Would you like me to create a shopping list for these meals?"""

    second_response = """Absolutely! Here's a delicious and safe Mediterranean breakfast option that aligns with your preferences and dietary needs:

Mediterranean Veggie Omelet

Ingredients:
- 2 large eggs
- 1/2 cup chopped spinach
- 1/4 cup diced tomatoes
- 1/4 cup diced bell peppers (any color you prefer)
- 1/4 cup feta cheese (crumbled)
- 1 tablespoon olive oil
- Salt and pepper to taste

Instructions:
1. In a bowl, whisk together the eggs, salt, and pepper.
2. Heat the olive oil in a nonstick skillet over medium heat.
3. Add the bell peppers and tomatoes to the skillet, and sauté for about 2 minutes.
4. Add the spinach, cooking until wilted (about 1 minute).
5. Pour in the whisked eggs over the veggies and cook until the edges start to set.
6. Sprinkle the feta cheese on top, then gently fold the omelet in half.
7. Cook for another minute until the eggs are fully set.

Serve this with a side of sliced cucumber or some fresh fruit like a medium peach or 1/2 cup of berries for a balanced meal that's satisfying and blood sugar-friendly.

Would you like me to create a shopping list for these meals?"""

    print("🔍 DETAILED PROFILE INTEGRATION ANALYSIS")
    print("=" * 60)
    
    # User profile data that should be integrated
    user_profile = {
        "diabetes_type": "type2",
        "allergies": ["nuts", "shellfish"],
        "food_preferences": ["mediterranean", "low_carb"],
        "health_goals": ["blood_sugar_control", "weight_loss"]
    }
    
    print(f"👤 User Profile:")
    for key, value in user_profile.items():
        print(f"   - {key}: {value}")
    
    print(f"\n📝 FIRST RESPONSE ANALYSIS:")
    print(f"Response length: {len(first_response)} characters")
    
    # Check for diabetes awareness
    diabetes_terms = ["diabetes", "blood sugar", "glucose", "type 2", "type2"]
    found_diabetes = [term for term in diabetes_terms if term.lower() in first_response.lower()]
    print(f"✅ Diabetes awareness: {found_diabetes}")
    
    # Check for health goals integration
    health_goal_terms = ["blood sugar control", "weight loss"]
    found_goals = [goal for goal in health_goal_terms if goal.lower() in first_response.lower()]
    print(f"✅ Health goals integration: {found_goals}")
    
    # Check for allergy awareness (should avoid nuts and shellfish)
    allergy_terms = ["nuts", "shellfish", "nut", "allergy", "allergic"]
    found_allergies = [term for term in allergy_terms if term.lower() in first_response.lower()]
    print(f"⚠️  Allergy awareness: {found_allergies} (Expected: nuts/shellfish avoidance)")
    
    # Check for Mediterranean diet preferences
    mediterranean_terms = ["mediterranean", "olive oil", "feta", "olives"]
    found_mediterranean = [term for term in mediterranean_terms if term.lower() in first_response.lower()]
    print(f"✅ Mediterranean preferences: {found_mediterranean}")
    
    # Check for low-carb preferences
    lowcarb_terms = ["low carb", "low-carb", "moderation", "limit", "whole grains"]
    found_lowcarb = [term for term in lowcarb_terms if term.lower() in first_response.lower()]
    print(f"✅ Low-carb awareness: {found_lowcarb}")
    
    # Check for imperial measurements
    imperial_terms = ["cup", "cups", "tablespoon", "tablespoons", "ounces", "oz"]
    found_imperial = [term for term in imperial_terms if term.lower() in first_response.lower()]
    print(f"✅ Imperial measurements: {found_imperial}")
    
    print(f"\n📝 SECOND RESPONSE ANALYSIS:")
    print(f"Response length: {len(second_response)} characters")
    
    # Check for Mediterranean diet response
    mediterranean_second = ["mediterranean", "olive oil", "feta", "tomatoes", "spinach"]
    found_med_second = [term for term in mediterranean_second if term.lower() in second_response.lower()]
    print(f"✅ Mediterranean diet response: {found_med_second}")
    
    # Check for allergy safety (no nuts or shellfish mentioned)
    unsafe_ingredients = ["nuts", "shellfish", "almond", "walnut", "peanut", "shrimp", "crab", "lobster"]
    found_unsafe = [term for term in unsafe_ingredients if term.lower() in second_response.lower()]
    if found_unsafe:
        print(f"❌ UNSAFE INGREDIENTS FOUND: {found_unsafe}")
    else:
        print(f"✅ Allergy safety: No nuts or shellfish ingredients detected")
    
    # Check for imperial measurements in recipe
    imperial_second = ["cup", "cups", "tablespoon", "tablespoons"]
    found_imperial_second = [term for term in imperial_second if term.lower() in second_response.lower()]
    print(f"✅ Imperial measurements in recipe: {found_imperial_second}")
    
    # Check for diabetes-friendly language
    diabetes_friendly = ["blood sugar", "balanced", "satisfying"]
    found_diabetes_friendly = [term for term in diabetes_friendly if term.lower() in second_response.lower()]
    print(f"✅ Diabetes-friendly language: {found_diabetes_friendly}")
    
    print(f"\n📊 PROFILE INTEGRATION SUMMARY:")
    
    integration_score = 0
    total_checks = 8
    
    # Score each aspect
    if found_diabetes: 
        integration_score += 1
        print("✅ Diabetes awareness: INTEGRATED")
    else:
        print("❌ Diabetes awareness: NOT INTEGRATED")
    
    if found_goals:
        integration_score += 1
        print("✅ Health goals: INTEGRATED")
    else:
        print("❌ Health goals: NOT INTEGRATED")
    
    if found_mediterranean or found_med_second:
        integration_score += 1
        print("✅ Mediterranean preferences: INTEGRATED")
    else:
        print("❌ Mediterranean preferences: NOT INTEGRATED")
    
    if found_lowcarb:
        integration_score += 1
        print("✅ Low-carb preferences: INTEGRATED")
    else:
        print("❌ Low-carb preferences: NOT INTEGRATED")
    
    if found_imperial or found_imperial_second:
        integration_score += 1
        print("✅ Imperial measurements: INTEGRATED")
    else:
        print("❌ Imperial measurements: NOT INTEGRATED")
    
    if not found_unsafe:
        integration_score += 1
        print("✅ Allergy safety: INTEGRATED (no unsafe ingredients)")
    else:
        print("❌ Allergy safety: NOT INTEGRATED (unsafe ingredients found)")
    
    if "Would you like me to create a shopping list" in first_response or "Would you like me to create a shopping list" in second_response:
        integration_score += 1
        print("✅ Shopping list offer: INTEGRATED")
    else:
        print("❌ Shopping list offer: NOT INTEGRATED")
    
    if found_diabetes_friendly:
        integration_score += 1
        print("✅ Diabetes-friendly language: INTEGRATED")
    else:
        print("❌ Diabetes-friendly language: NOT INTEGRATED")
    
    success_rate = (integration_score / total_checks) * 100
    print(f"\n🎯 FINAL INTEGRATION SCORE: {integration_score}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 EXCELLENT PROFILE INTEGRATION - AI is successfully using user profile data!")
        return True
    elif success_rate >= 50:
        print("⚠️  GOOD PROFILE INTEGRATION - AI is using some profile data but could be improved")
        return True
    else:
        print("❌ POOR PROFILE INTEGRATION - AI is not effectively using user profile data")
        return False

if __name__ == "__main__":
    analyze_ai_response_for_profile_integration()