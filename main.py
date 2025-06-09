import json


def extract_pdfnames_from_response(filename: str) -> list[str]:
    """
    Extracts the list of 'pdfname' values from a JSON file with a nested structure:

    Args:
        filename (str): The path to the JSON file.

    Returns:
        list[str]: A list containing all pdfname strings found inside 'items'.
                   Returns an empty list if none are found or on invalid structure.
    """

    # Open the JSON file in read mode with UTF-8 encoding
    with open(filename, "r", encoding="utf-8") as file:
        # Parse JSON content into a Python dictionary
        data = json.load(file)

    # Access the 'response' key safely; returns empty dict if missing
    response = data.get("response", {})

    # From 'response', get the 'items' list; default to empty list if missing
    items = response.get("items", [])

    # Check if 'items' is really a list (expected type)
    if not isinstance(items, list):
        print("Error: 'items' key is not a list.")
        return []

    # Iterate over each dictionary in 'items' list
    # Extract the value of 'pdfname' if it exists in that dictionary
    pdf_names: list[str] = [item.get("pdfname") for item in items if "pdfname" in item]

    # Return the list of pdfname strings
    return pdf_names


if __name__ == "__main__":
    # Call the function and assign the returned list to pdf_list
    pdf_list = extract_pdfnames_from_response("api_response.json")

    # Print the entire list of extracted pdfnames
    print(pdf_list)
