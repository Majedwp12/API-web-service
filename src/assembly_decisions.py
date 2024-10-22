import json
import xml.etree.ElementTree as ET
import pandas as pd
import requests


def get_assembly_decisions_data(ins_code):
    try:
        # Request to fetch the data
        res = requests.get(f'https://cdn.tsetmc.com/api/Codal/GetStatementContentByInsCode/14/0/-1/{ins_code}')
        res.raise_for_status()  # Will raise an exception for HTTP errors

        new_data = res.json()
        # Check if 'statemetnContent' exists in the JSON data
        if 'statemetnContent' not in new_data:
            raise ValueError("Missing 'statemetnContent' in the JSON data.")

        extended_extracted_data = []

        # Loop through the statement content and extract the required fields
        for statement in new_data['statemetnContent']:
            content_xml = statement.get('content', None)
            publish_date = statement.get('publishDateTime_DEven', None)
            title = statement.get('title', None)

            if content_xml is None:
                continue  # Skip if no content XML available

            try:
                # Parse the XML content
                root = ET.fromstring(content_xml)

                # Extract shareholders and presidium members if present
                shareholders = root.find('AssemblyShareHolder')
                presidium = root.find('Presidium')

                # Extract shareholders details
                if shareholders is not None:
                    for shareholder in shareholders:
                        extended_extracted_data.append({
                            'Title': title,
                            'PublishDate': publish_date,
                            'Type': 'Shareholder',
                            'Name': shareholder.find('td[1]').text if shareholder.find('td[1]') is not None else None,
                            'Shares': shareholder.find('td[2]').text if shareholder.find('td[2]') is not None else None,
                            'Percentage': shareholder.find('td[3]').text if shareholder.find(
                                'td[3]') is not None else None
                        })

                # Extract presidium members details
                if presidium is not None:
                    for member in presidium:
                        extended_extracted_data.append({
                            'Title': title,
                            'PublishDate': publish_date,
                            'Type': 'Presidium Member',
                            'Member': member.text if member is not None else None
                        })


            except ET.ParseError as e:
                print(f"Error parsing XML content for ins_code {ins_code}: {e}")
                continue

        # If no data is extracted, return an empty DataFrame
        if not extended_extracted_data:
            print(f"No board members found for ins_code {ins_code}.")
            return pd.DataFrame()

        # Convert list of dictionaries to DataFrame
        df_extended_extracted = pd.DataFrame(extended_extracted_data)
        return df_extended_extracted

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return pd.DataFrame()

    except ValueError as e:
        print(f"Value error: {e}")
        return pd.DataFrame()


# Example usage
# ins_code = 71483646978964608
# df = extract_shareholders_and_presidium(ins_code)
# print(df)
