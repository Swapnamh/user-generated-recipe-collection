from recipes.models import Recipe, Category

breakfast = Category.objects.get(name="Breakfast")
lunch = Category.objects.get(name="Lunch")
dinner = Category.objects.get(name="Dinner")
dessert = Category.objects.get(name="Dessert")

category_keywords = {
    breakfast: ["paratha", "poha", "dosa", "egg", "scrambled eggs"],
    lunch: ["biryani", "rajma", "pulao", "dal", "sambar", "chole", "bhature", "rice", "curry", "steamed rice", "vegetable pulao"],
    dinner: ["lasagna", "chicken", "pasta", "maggie", "grilled chicken", "vegetable lasagna", "spicy maggie noodles"],      
    dessert: ["cake", "halwa", "gulab", "jamun", "chocolate lava cake", "gajar halwa", "gulab jamun"],
}

for recipe in Recipe.objects.all():
    title = recipe.title.lower()
    assigned = False
    for category, keywords in category_keywords.items():
        if any(keyword in title for keyword in keywords):
            recipe.category.set([category])
            assigned = True
            break
    if not assigned:
        recipe.category.set([lunch])  # fallback category

    recipe.is_for_sale = True
    recipe.save()

    print(f"Updated: {recipe.title} -> {[c.name for c in recipe.category.all()]}, for sale: {recipe.is_for_sale}")
