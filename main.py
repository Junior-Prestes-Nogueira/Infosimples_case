from script import case_infosimples as workflow
                              

if __name__ == '__main__':    
    # Request data and create object soup
    soup = workflow.get_page_html()

    # Collecting data:
    title = workflow.get_title(soup)
    brand = workflow.get_brand(soup)
    categories = workflow.get_categories(soup)
    description = workflow.get_description(soup)
    sku = workflow.get_sku(soup)
    properties = workflow.get_properties(soup)
    reviews = workflow.get_reviews(soup)
    reviews_average_score = workflow.get_reviews_average_score(soup)
    url = workflow.get_url(soup)

    # resposta
    workflow.resposta_final(title, brand, categories, description, sku, properties, reviews, reviews_average_score, url)

