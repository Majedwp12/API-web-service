import requests
import json
import xml.etree.ElementTree as ET
import pandas as pd

def get_board_members(ins_code):
    try:
        # Request to fetch the data
        res = requests.get(f'https://cdn.tsetmc.com/api/Codal/GetStatementContentByInsCode/12/0/-1/{ins_code}')
        res.raise_for_status()  # Will raise an exception for HTTP errors

        data = res.json()

        # Check if 'statemetnContent' key exists in the JSON data
        if 'statemetnContent' not in data:
            raise ValueError("Missing 'statemetnContent' in the response data.")

        extracted_data = []

        # Loop through the statement content and extract the required fields
        for statement in data['statemetnContent']:
            content_xml = statement.get('content', None)
            publish_date = statement.get('publishDateTime_DEven', None)
            title = statement.get('title', None)

            if content_xml is None:
                continue  # Skip if no content XML available

            try:
                # Parse the XML content
                root = ET.fromstring(content_xml)
                board_members = root.find('BoardMembers')

                if board_members is None:
                    continue  # Skip if no board members data in the XML

                # Extract BoardMember information into a list of dictionaries
                for member in board_members:
                    extracted_data.append({
                        'Agent': member.find('Agent').text if member.find('Agent') is not None else None,
                        'EducationDegree': member.find('EducationDegree').text if member.find('EducationDegree') is not None else None,
                        'Charged': member.find('Charged').text if member.find('Charged') is not None else None,
                        'NationalCode_RegisterNumber': member.find('NationalCode_RegisterNumber').text if member.find('NationalCode_RegisterNumber') is not None else None,
                        'MemberName': member.find('MemberName').text if member.find('MemberName') is not None else None,
                        'PreviuosAgent': member.find('PreviuosAgent').text if member.find('PreviuosAgent') is not None else None,
                        'PreviousMemberName': member.find('PreviousMemberName').text if member.find('PreviousMemberName') is not None else None,
                        'Designation': member.find('Designation').text if member.find('Designation') is not None else None,
                        'Title': title,
                        'PublishDate': publish_date
                    })

            except ET.ParseError as e:
                print(f"Error parsing XML content for ins_code {ins_code}: {e}")
                continue

        if not extracted_data:
            print(f"No board members found for ins_code {ins_code}.")
            return pd.DataFrame()

        # Convert list of dictionaries to DataFrame
        df_extracted = pd.DataFrame(extracted_data)
        return df_extracted

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return pd.DataFrame()

    except ValueError as e:
        print(f"Value error: {e}")
        return pd.DataFrame()

