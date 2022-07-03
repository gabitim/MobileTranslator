/* eslint-disable prettier/prettier */
import React from 'react';

import FontAwesome from 'react-native-vector-icons/FontAwesome';
import {StyleSheet} from 'react-native';
import SelectDropdown from 'react-native-select-dropdown';

const options = [
  {
    label: 'Textract',
    value: 'Textract',
  },
  {
    label: 'MyCustomOcr',
    value: 'MyCustomOcr',
  },
];

const OcrSelector = ({setOcrOption}) => {
  return (
    <SelectDropdown
      defaultButtonText="Ocr option"
      buttonStyle={styles.button}
      buttonTextStyle={styles.buttonText}
      renderDropdownIcon={isOpened => {
        return <FontAwesome name={isOpened ? 'chevron-up' : 'chevron-down'} color={'#444'} size={18} />;
      }}
      dropdownIconPosition={'right'}
      data={options}
      onSelect={(selectedItem) => setOcrOption(selectedItem.value)}
      buttonTextAfterSelection={(selectedItem) => selectedItem.label }
      rowTextForSelection={(item) => item.label}
    />
  );
};

const styles = StyleSheet.create({
  button: {
    width: 220,
    backgroundColor: '#0099ff',
    alignSelf: 'center',
  },
  buttonText: {
    color: '#ffffff',
  },
});

export default OcrSelector;
