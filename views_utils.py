from models import Product, Option
import copy


def getPostValue(request, value):
    if value in request.POST:
        return request.POST[value]
    else:
        return None

def findDuplicateDictInList(dict_compare, dict_list, ignore_keys = []):
    dict_compare_tmp = copy.deepcopy(dict_compare)
    for key in ignore_keys:
        del dict_compare_tmp[key]
    for dict_item in dict_list:
        #Creating a copy of the dictionar to prevent affecting the original
        dict_item_tmp = copy.deepcopy(dict_item)
        for key in ignore_keys:
            del dict_item_tmp[key]
        shared_items = set(dict_compare_tmp.items()) & set(dict_item.items())
        if len(shared_items) == len(dict_compare_tmp):
            return True
    return False

#Adds the total of all accessories and options
def getProductTotal(product, accessories, options):
    accessory_price = 0
    option_price = 0
    for accessory in accessories:
        if accessory.price is not None:
            accessory_price = accessory_price + accessory.total()
    for option in options:
        if option.price is not None:
            option_price = option_price + option.price
    return product.total() + accessory_price + option_price

def setProducts(cart):
    products = []
    for item in cart:
        product = Product.objects.get(pk=item['product_id'])
        accessories = [getModelObject(Product, item['accessories'])]
        options = [getModelObject(Option, item['options'])]
        price = getProductTotal(product, accessories, options)
        products.append({
            "session": item,
            "product": product,
            "accessories": accessories,
            "options": options,
            "price": price
            })
    return products

def getModelObject(object, object_id):
    try:
        return object.objects.get(pk=object_id)
    except object.DoesNotExist:
        return None
    except KeyError:
        return None
