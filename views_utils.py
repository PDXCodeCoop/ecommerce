from models import Product, Option
import copy


def getPostValue(request, value):
    if value in request.POST:
        return request.POST[value]
    else:
        return None

def getPostList(request, value):
    if value in request.POST:
        return request.POST.getlist(value)
    else:
        return None

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same

def findDuplicateDictInList(dict_compare, dict_list, ignore_keys = []):
    dict_compare_tmp = copy.deepcopy(dict_compare)
    for key in ignore_keys:
        del dict_compare_tmp[key]
    for dict_item in dict_list:
        #Creating a copy of the dictionar to prevent affecting the original
        dict_item_tmp = copy.deepcopy(dict_item)
        for key in ignore_keys:
            del dict_item_tmp[key]
        d1 = dict_compare_tmp
        d2 = dict_item_tmp
        d1_keys = set(d1.keys())
        d2_keys = set(d2.keys())
        intersect_keys = d1_keys.intersection(d2_keys)
        same = set(o for o in intersect_keys if d1[o] == d2[o])
        if (len(same) == len(dict_compare_tmp)):
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
        accessories = []
        for accessory in item['accessories']:
            accessories.append(getModelObject(Product, accessory))
        options = []
        for option in item['options']:
            options.append(getModelObject(Option, option))
        product = Product.objects.get(pk=item['product_id'])
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
