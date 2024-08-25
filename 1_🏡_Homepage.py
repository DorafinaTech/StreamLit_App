import streamlit as st
import csv
import os
import json5
import json
import random
import string
import requests
import re

print("Home Page")

# Gemini API key
api_key = "AIzaSyDDxAPEJLzzIWmrVjILfdRSmGnzpLKr6Ls"

csv_dataset_file_path = "./dataset.csv"

# Misc functions

# Generate a random alphanumeric string of length 5


def generate_uid():
    return "".join(random.choices(string.ascii_letters + string.digits, k=5))


def search_result_row(product, other_results=[]):
    col1, col2 = st.columns([1, 4])
    
    other_results = [item for item in other_results if item.get("product_uid") != product["product_uid"]]

    with col1:
        st.image(product["product_image_url"], width=100)
    with col2:
        st.subheader(product["product_name"])

        if st.button("View", key=product["product_uid"]):

            st.session_state["product"] = product
            st.session_state["other_search_results"] = other_results

            st.switch_page("pages/2_🛒_Product_Page.py")


# Function to search for products


def clear_console():
    # For Windows
    if os.name == "nt":
        os.system("cls")
        # For Linux and Mac
    else:
        os.system("clear")

    print("console cleared!!!")


# @st.experimental_memo
def run_model_recommendation(search_term):
    clear_console()

    # Read the CSV file content
    csv_content = ""
    with open(csv_dataset_file_path, "r") as csv_file:
        csv_content_lines = csv_file.readlines()
        # Joining CSV content with escaped newlines to insert into JSON
        csv_content = "\\n".join([line.strip() for line in csv_content_lines])

        prompt = """Train on this CSV,

                --start training here--
                {csv_content}
                --end training here---

                Take the role of a recomendation system,
                Using your training data, when asked \"search term '<the search term or query>'\", produce the json result.
                Limit results to a maximum of 10 items.

                DON'T truncate the matches for brevity or any other reason, strictly.
                If the matches are too much, only include the matches that you can output in the json response.
                Don't add any text like 'other matches truncated for response brevity' so the json remains valid, strictly.
                Limit results to not more than 20 items to keep it brief.

                Search results should be from the training CSV only. return an empty array if there's no result.
                
                Produce the output in this format, a JSON array:
                
                Search results:
                ```
                [
                        {
                        "product_uid":"{the valid product uid from your training data",
                        "product_name":"{the valid product name from your training data",
                        "product_description":"{the product description from your training data",
                        "product_image_url":"{the valid product image url from your training data. It 'SHOULD' point to a valid image url, or a placeholder image otherwise, which 'MUST' also be a valid URL",
                        "product_image_visual_description": "the visual description of the image, you can try loading the image, then try describing it"
                        "search_relevance_score": "<the score, guess the score based on the relevance of the search result, MUST be a valid floating point number between 0.0 and 1.0>",
                        "reason_for_recommendaion": "<the reason for commending this product for the given search query>",
                        "related_items": [
                            # NOTE that this field is mandatory, and if there are no related products, recommend items that may be closely similar, forexample, hammer is related to nail, Refrigerator is related to fridge, or just an empty array, .
                            # No more than 5 related items similar in structure to this parent item, related contecxtually baed on relevance, or product name or descripion, processed with natural language.
                            # They MUST not have the 'related_items' property so we don't do nesting, on that note, there STRICTLY should be no tailing coma after `reason_for_recommendaion` so the JSON remains valid.s
                            # Remember, related items shold hve the same structure as the parent object except for the 'related_items' field, but they should have product_uid, product_name, product_description, product_image_url, product_image_visual_description, product_image_visual_description, search_relevance_score, and reason_for_recommendaion.
                            ]
                        },
                        ... other matches ...
                    ]
                    ```
                """.replace(
            "{csv_content}", csv_content
        )

        # print("-- Begin prompt: --")
        # print(prompt)
        # print("-- End prompt: --")

        query = f"search term '{search_term}'"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={api_key}"
        # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}

        data = {
            # "contents": [
            #     {
            #     "role": "user",
            #     "parts": [
            #         {
            #             "text": f"{prompt}"
            #             # "text": "Hello"
            #         }
            #     ]
            #     },
            #     {
            #     "role": "model",
            #     "parts": [
            #         {
            #         "text": """
            #             Search term 'heater'
            #             Search results:
            #             json```
            #             [
            #                 {
            #                     "product_uid": "180158",
            #                     "product_name": "ProCom 80,000 BTU Portable Single Convection Heater",
            #                     "product_description": "ProCom Heating's Portable Convection Outdoor Propane Heaters, also referred to as \"trash can\" heaters in the trade, offer an inexpensive solution for temporary space heating especially for applications where there is no electricity. Compact, lightweight and clean burning, these heaters also feature a 360 heating radius which allows quick and efficient hot air distribution. These commercial grade heaters offer a perfect solution for temporary heating jobs such as garages, construction sites, warehouses, agricultural and industrial applications.California residents: see&nbsp;Proposition 65 information80,000 BTU variable convection heaters3 heat settings - 40,000, 60,000 and 80,000 BTUCirculates convection heat 360 in a degree radiusHeats up to 1,800 sq. ft.No electricity requiredPiezo matchless ignitionCSA  certifiedIncludes 10 ft. hose and regulatorHome Depot Protection Plan:",
            #                     "product_image_url": "https://m.media-amazon.com/images/I/61gMG2vP5ML.jpg",
            #                     "product_image_visual_description": "A large, cylindrical silver propane heater with a carrying handle on top and a hose attached at the side. It looks sturdy and suitable for outdoor use, such as in a construction site or warehouse.",
            #                     "search_relevance_score": "0.95",
            #                     "reason_for_recommendaion": "This product matches the search term 'heater' with high relevance due to its primary function as a portable convection heater. It's designed for temporary space heating in locations without electricity, making it highly suitable for outdoor or construction site use.",
            #                     "related_items": [
            #                         {
            #                             "product_uid": "180159",
            #                             "product_name": "6 ft. x 8 ft. Pressure-Treated Pine Shadowbox Fence Panel",
            #                             "product_description": "Use the 6 ft. x 8 ft. Pressure Treated Spruce Shadowbox Fence Panel to help provide privacy in your yard. This panel is made of solid unpainted spruce, and is treated to provide resistance to termites and fungal decay. It can also be stained or painted as you see fit.California residents: see&nbsp;Proposition 65 informationPressure treated for long lifeNatural wood appearance can be stained or painted to suit your locationDesigned to enhance the appearance of your yardPanel measures 8 ft. wideNote: Product may vary by store",
            #                             "product_image_url": "https://images.thdstatic.com/productImages/bb44947e-4243-45ba-ab5c-3b02b1bd4f83/svn/wood-wood-fence-panels-118830-a0_600.jpg",
            #                             "product_image_visual_description": "A large wooden fence panel made of pressure-treated pine in a shadowbox design, providing privacy and aesthetic appeal to any yard. The wood's natural color is visible, and it looks durable and ready for outdoor installation.",
            #                             "search_relevance_score": "0.2",
            #                             "reason_for_recommendaion": "While not directly related to heaters, customers looking for outdoor heating solutions might also be interested in outdoor construction and yard improvements like fencing."
            #                         }
            #                     ]
            #                 }
            #             ]
            #             ```
            #             """
            #         }
            #         # {
            #         #     "text":"Hi"
            #         # }
            #     ]
            #     },
            #     {
            #     "role": "user",
            #     "parts": [
            #         {
            #         "text": f"{query}"
            #         # "text": "Holla"
            #         }
            #     ]
            #     }
            # ],
            "contents": data_preparation()
            + [{"role": "user", "parts": [{"text": f"{query}"}]}],
            "generationConfig": {
                # "temperature": 0.9,
                "temperature": 0.2,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048,
                "stopSequences": [],
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ],
        }

        # Specify the file name
        file_name = "data.json"  # Writing the dictionary to a file in JSON format
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

        requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:updateRankingParams?key={api_key}",
            headers=headers,
            data=json.dumps(
                {
                    "rankingParams": {
                        "diversityLevel": "medium",
                        "deduplicationStrategy": "exact",
                    }
                }
            ),
        )

        response = requests.post(url, headers=headers, data=json.dumps(data))

        result = json5.loads(response.text)

        print("Gemini Raw Response: ", response.text)

        # response = result["candidates"][0]["content"]["parts"][0]["text"]
        response = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", '[]')

        print("Gemini Parsed Response: ", response)

        return response


def search_products(query):
    raw_result = run_model_recommendation(query)
    raw_result = (
        raw_result.replace("Search results:", "")
        .replace("```json", "")
        .replace("```", "")
        .replace("```", "")
        .replace("json", "")
        .replace("`", "")
    )
    
    # response = response.replace("\n", "\\n")
    # response = response.replace("\\", "\\\\")
    raw_result = re.sub(r'(?<=")[^"]*?(?<!\\)\\n[^"]*?(?=")', lambda match: match.group(0).replace('\\n', '\\\\n'), raw_result)
    raw_result = raw_result.replace("\n", " ")

    clear_console()
    print("raw_result: ", raw_result)

    result = json5.loads(raw_result)
    
    # Filter out products with a relevance score less than or equal to 0.1
    result = filter(lambda x: x["search_relevance_score"] > 0.1, result)
    
    # Sort the filtered products by relevance score in descending order
    result = sorted(result, key=lambda x: x["search_relevance_score"], reverse=True)

    return result


# Main page function with product search and enhanced display


def main_page():
    st.title("Enhanced Home Depot Search Platform")
    query = st.text_input("Search for products", on_change=clear_product_selection)

    if query:
        results = search_products(query)

        if results:
            for product in results:
                search_result_row(product, results)

        else:
            st.warning(
                "No products found matching your search. Please try again with a different query."
            )


# Helper function to clear product selection when initiating a new search


def clear_product_selection():
    if "product" in st.session_state:
        del st.session_state["product"]


def data_preparation():
    # Define your original and new CSV file paths
    original_csv_path = "./dataset.csv"
    transformed_csv_path = "./transformed-dataset_do_not_edit_directly.csv"

    extra_prompts = [
        {
            "input": (
                "Train on the above data,\n\n"
                + "Take the role of a recomendation system,\n\n"
                + "Using your training data, when asked `search term '<the search term or query from the user>'`\",\n"
                + "Use your natural language ability to read the training data above and find exact, close, and related matches,\n"
                + "e.g \"search term 'something for keeping food cold'\" is same as \"search term 'fridge'\"\n"
                + "Produce the result as a json array of objects with the following fields: product_uid, product_name, product_description, product_image_url, product_image_visual_description, search_relevance_score, reason_for_recommendaion, related_items \n\n"  # + "Produce the json result in the format:\n\n"
                # + "Search results:\n"
                # + "json```"
                # + " [\n"
                # + "     {\n"
                # + '         "product_uid": string,\n'
                # + '         "product_name": string,\n'
                # + '         "product_description": string\n'
                # + '         "product_image_url": string\n'
                # + '         "product_image_visual_description": string\n'
                # + '         "search_relevance_score": float between 0.1 and 1.0\n'
                # + '         "reason_for_recommendaion": string\n'
                # + '         "related_items": array\n'
                # + "     },\n"
                # + "     ...others\n"
                # + " ]\n"
                # + "```"
                + "DO NOT try to truncate the matches for brevity or any other reason, strictly.\n"
                + "If the matches are too much, only include the matches that you can output in the json response.\n"
                + "Don't add any text like 'other matches truncated for response brevity' so the json remains valid, strictly.\n"
                + "Limit results to not more than 20 items to keep it brief.\n\n"
                + "Search results should be from the training CSV only. return an empty array if there's no result."
            ),
            "output": "Okay, let's give it a try, prompt me with your search term, you can try \"search term 'heater'\" or anything else",
        },
        {
            "input": "search term 'something for keeping food cold'",
            "output": (
                "Search results:\n"
                + "json```"
                + "[\n"
                + "    {\n"
                + '        "product_uid": "102820",\n'
                + '        "product_name": "Magic Chef 3.5 cu. ft. Mini Refrigerator in Stainless Look, ENERGYSTAR",\n'
                + '        "product_description": "Whether you\'re college-bound or simply want a little extra refrigerator space in your home, this Magic Chef 3.5 cu. ft. Compact Refrigerator has the storage options you\'re looking for. The sleek appearance is matched by its well-designed interior a can dispenser conveniently keeps soda in the door while additional door shelves provide space for other frequently used items. Glass refrigerator shelves are easy to clean.\nEnergy Star qualified - meets or exceeds federal guidelines for energy efficiency, which means year-round energy savings\nUpfront Interior analog controls for making quick adjustments to internal temperature\n3 fresh-food shelves provide storage for both larger items and smaller items to efficiently utilize interior capacity\nDoor shelves help you keep frequently used items up front for easy access\nCan dispenser keeps soda cans neat and convenient\n3.5 cu. ft. capacity mini refrigerator is manual defrost\nFull width freezer compartment allows for freezing of smaller frozen food items\nInterior light for easy viewing of stored items\nWarranty is 1 Year Parts and Labor; 5 Years on compressor (parts only)\nThis item does not qualify for the Major Appliance Delivery and Haul Away or Installation Services\nThis item does not qualify for the Major Appliance Delivery and Haul Away or Installation Services\nHome Depot Protection Plan:",\n'
                + '        "product_image_url": "https://i5.walmartimages.com/asr/97014d40-b492-4ca5-9148-cead091c2f5b.09968b47cff8f0fa9c2adbf2163d5408.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF",\n'
                + '        "product_image_visual_description": "",\n'
                + '        "search_relevance_score": 1.0,\n'
                + '        "reason_for_recommendaion": "This mini refrigerator is specifically designed to keep food cold, matching the search term \'something for keeping food cold\'.",\n'
                + '        "related_items": []\n'
                + "    }\n"
                + "]\n"
                + "```"
            ),
        },
        {
            "input": "search term 'Nails'",
            "output": (
                "Search results:\n"
                + "json```"
                + "[\n"
                + "    {\n"
                + '        "product_uid": "102817",\n'
                + '        "product_name": "Hitachi 7/8 in. x 0.120 in. Full Round-Head Smooth Shank Electro Galvanized Wire Coil Roofing Nails (7,200-Pack)",\n'
                + '        "product_description": "The Full Round-Head Smooth Shank Wire Coil Electro-Galvanized Roofing Nails fit Hitachi NV45AB, NV45AB2, NV45AB2S, NV45AE and NV45AES roofing nailers. These nails have a smooth shank with an Electro-Galvanized finish. This item is 7/8 in. in length x 0.120 in. in diameter and comes in a (7,200-pack). Every Hitachi accessory is designed to the highest standards and is rigorously tested for both performance and durability. Since its inception, Hitachi has pioneered innovative technologies that have improved the quality of craftsmanship worldwide. Hitachi is a leader in power tool research and development and has achieved many firsts in the power tool industry. Today, Hitachi continues the tradition of innovation and engineering with new features in addition to classic quality.\nFull round-head wire coil electro-galvanized roofing nails\nFits Hitachi NV45AB, NV45AB2, NV45AB2S, NV45AE and NV45AES roofing nailers\nNails have a smooth shank and an electro-galvanized finish\nHas a 7/8 in. length x 0.120 in. diameter and comes in a 7,200-pack",\n'
                + '        "product_image_url": "https://m.media-amazon.com/images/I/81UiDXjGrWL._AC_UF894,1000_QL80_.jpg",\n'
                + '        "product_image_visual_description": "",\n'
                + '        "search_relevance_score": 1.0,\n'
                + '        "reason_for_recommendaion": "This product directly matches the search term `Nail` as it is a pack of roofing nails.",\n'
                + '        "related_items": []\n'
                + "    }\n"
                + "]\n"
                + "```"
            ),
        },
    ]

    # Open the original CSV file and the new file where the transformed data will be written
    with open(original_csv_path, mode="r", encoding="utf-8") as infile, open(
        transformed_csv_path, mode="w", newline="", encoding="utf-8"
    ) as outfile:

        # Create CSV reader and writer
        reader = csv.DictReader(infile)
        fieldnames = ["input", "output"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write the header to the new CSV
        writer.writeheader()

        # Iterate through each row of the original CSV
        for row in reader:
            # Construct the input string using the product details
            input_text = (
                "Consider a product with the following details: "
                + f"product_uid: {row['product_uid']}; "
                + f"product_name: {row['product_name']}; "
                + f"product_description: {row['product_description']}; "
                + f"product_image_url: {row['product_image_url']}; "
                + f"product_image_visual_description: {row['product_image_visual_description']}. "
                + f"What is the product description?"
            )

            # The output is the product_description from the current row
            output_text = row["product_description"]

            # Write the transformed data to the new CSV
            writer.writerow({"input": input_text, "output": output_text})

            # end for

        # Write extra hardcoded rows from the "extra_prompts" array
        for prompt in extra_prompts:
            writer.writerow({"input": prompt["input"], "output": prompt["output"]})

        # end with

    # After writing, read the transformed file and return its content
    # transformed_csv_content = ""
    # with open(transformed_csv_path, mode='r', encoding='utf-8') as transformed_file:
    #     transformed_csv_content = transformed_file.read()

    response_structure = []
    # After processing the CSV file, append interactions from it
    with open(transformed_csv_path, mode="r", encoding="utf-8") as transformed_file:
        reader = csv.DictReader(transformed_file)

        for row in reader:
            user_input = {"role": "user", "parts": [{"text": row["input"]}]}
            model_response = {"role": "model", "parts": [{"text": row["output"]}]}

            # Append the user input and model response to the response structure
            response_structure.extend([user_input, model_response])

    return response_structure


if __name__ == "__main__":
    # Initialize session state for navigation
    if "navigation" not in st.session_state:
        st.session_state["navigation"] = "Home"

    main_page()
