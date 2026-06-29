from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Min, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, FoodItemForm, RestaurantForm
from .models import Category, FoodItem, Restaurant


def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url='login'
    )(view_func)


def home(request):
    available_foods = Q(
        foods__is_available=True,
        foods__category__is_active=True,
    )
    restaurant_queryset = Restaurant.objects.filter(is_open=True).annotate(
        menu_count=Count('foods', filter=available_foods),
        starting_price=Min('foods__price', filter=available_foods),
    ).order_by('-rating')
    restaurants = restaurant_queryset[:6]

    food_queryset = FoodItem.objects.filter(
        is_available=True,
        restaurant__is_open=True
    ).select_related('restaurant', 'category').order_by('-rating')
    foods = food_queryset[:8]

    categories = Category.objects.filter(is_active=True)[:8]

    return render(request, 'home/home.html', {
        'restaurants': restaurants,
        'foods': foods,
        'categories': categories,
        'restaurant_count': restaurant_queryset.count(),
        'food_count': food_queryset.count(),
    })


def restaurant_list(request):
    available_foods = Q(
        foods__is_available=True,
        foods__category__is_active=True,
    )
    restaurants = Restaurant.objects.annotate(
        menu_count=Count('foods', filter=available_foods),
        starting_price=Min('foods__price', filter=available_foods),
    ).order_by('-rating')

    return render(request, 'restaurants/restaurants.html', {
        'restaurants': restaurants,
        'restaurant_count': restaurants.count(),
        'open_restaurant_count': restaurants.filter(is_open=True).count(),
    })


def search(request):
    query = request.GET.get('q', '').strip()

    available_foods = Q(
        foods__is_available=True,
        foods__category__is_active=True,
    )
    restaurants = Restaurant.objects.none()
    foods = FoodItem.objects.none()

    if query:
        restaurants = Restaurant.objects.filter(
            Q(name__icontains=query) |
            Q(cuisine_type__icontains=query) |
            Q(address__icontains=query) |
            Q(description__icontains=query)
        ).annotate(
            menu_count=Count('foods', filter=available_foods),
            starting_price=Min('foods__price', filter=available_foods),
        ).order_by('-is_open', '-rating', 'name')

        foods = FoodItem.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(restaurant__name__icontains=query) |
            Q(restaurant__cuisine_type__icontains=query),
            is_available=True,
            category__is_active=True,
            restaurant__is_open=True,
        ).select_related('restaurant', 'category').order_by('-rating', 'name')

    return render(request, 'restaurants/search_results.html', {
        'query': query,
        'restaurants': restaurants,
        'foods': foods,
        'restaurant_count': restaurants.count(),
        'food_count': foods.count(),
        'total_count': restaurants.count() + foods.count(),
    })


def food_list(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    foods = FoodItem.objects.filter(
        restaurant=restaurant,
        is_available=True,
        category__is_active=True
    ).select_related('category').order_by('category__name', 'name')

    categories = Category.objects.filter(
        foods__restaurant=restaurant,
        foods__is_available=True,
        is_active=True
    ).distinct()

    return render(request, 'restaurants/food_list.html', {
        'restaurant': restaurant,
        'foods': foods,
        'categories': categories,
        'food_count': foods.count(),
    })


def single_food(request, food_id):
    food = get_object_or_404(
        FoodItem.objects.select_related('restaurant', 'category'),
        id=food_id,
        is_available=True,
        restaurant__is_open=True,
        category__is_active=True,
    )

    return render(request, 'restaurants/singleFoodCard.html', {
        'singleFoodItem': food,
    })


@staff_required
def manager_dashboard(request):
    restaurants = Restaurant.objects.order_by('-created_at')

    foods = FoodItem.objects.select_related(
        'restaurant',
        'category'
    ).order_by('-created_at')

    categories = Category.objects.order_by('name')

    context = {
        'restaurant_count': restaurants.count(),
        'food_count': foods.count(),
        'category_count': categories.count(),
        'open_count': restaurants.filter(is_open=True).count(),
        'available_food_count': foods.filter(is_available=True).count(),
        'active_category_count': categories.filter(is_active=True).count(),

        'restaurants': restaurants[:5],
        'foods': foods[:6],
        'categories': categories[:6],
    }

    return render(request, 'dashboard/dashboard.html', context)


@staff_required
def add_restaurant(request):
    form = RestaurantForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            restaurant = form.save()
            messages.success(request, f'{restaurant.name} has been added successfully.')
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'dashboard/manager_form.html', {
        'form': form,
        'title': 'Add Restaurant',
        'subtitle': 'Create a new restaurant with cuisine type, address, rating, delivery time, status, and image.',
        'button_text': 'Save Restaurant',
    })


@staff_required
def add_category(request):
    form = CategoryForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            category = form.save()
            messages.success(request, f'{category.name} category has been added successfully.')
            return redirect('add_food')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'dashboard/manager_form.html', {
        'form': form,
        'title': 'Add Food Category',
        'subtitle': 'Create food categories like Biryani, Pizza, Desserts, Beverages, and Fast Food.',
        'button_text': 'Save Category',
    })


@staff_required
def add_food(request):
    form = FoodItemForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            food = form.save()
            messages.success(request, f'{food.name} has been added to the menu successfully.')
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'dashboard/manager_form.html', {
        'form': form,
        'title': 'Add Food Item',
        'subtitle': 'Attach the food item to a restaurant and category, then add price, veg/non-veg type, rating, image, and availability.',
        'button_text': 'Save Food Item',
    })
