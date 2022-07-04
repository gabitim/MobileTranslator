/* eslint-disable prettier/prettier */
import React from 'react';

import FontAwesome from 'react-native-vector-icons/FontAwesome';
import {StyleSheet} from 'react-native';
import SelectDropdown from 'react-native-select-dropdown';

export const ocrOptions = [
  {
    label: 'AWSTextract',
    value: 'AWSTextract',
  },
  {
    label: 'MyOcr',
    value: 'MyOcr',
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
      data={ocrOptions}
      defaultValue={ocrOptions[0]}
      onSelect={(selectedItem) => setOcrOption(selectedItem.value)}
      buttonTextAfterSelection={(selectedItem) => selectedItem.label }
      rowTextForSelection={(item) => item.label}
    />
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: 5,
    width: 130,
    height: 40,
    backgroundColor: 'gray',
    alignSelf: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 14,
  },
});

export default OcrSelector;
