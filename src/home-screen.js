/* eslint-disable prettier/prettier */
import React, {useState, useEffect} from 'react';

import {
  ActivityIndicator,
  Keyboard,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import {API, Auth, Storage} from 'aws-amplify';
import {launchImageLibrary, launchCamera} from 'react-native-image-picker';

import ImageUploader from './components/image-uploader';
import LanguageSelector, {languages} from './components/language-selector';
import OcrSelector, {ocrOptions} from './components/ocr-selector';

const api = 'api0a629dfb';
const path = '/translate';

const HomeScreen = () => {

  const [photo, setPhoto] = useState(null);
  const [language, setLanguage] = useState(languages[0].value);
  const [ocrOption, setOcrOption] = useState(ocrOptions[0].value);
  const [loading, setLoading] = useState(false);
  const [isKeyboardVisible, setKeyboardVisible] = useState(false);
  const [extractedText, setExtractedText] = useState('');
  const [translateText, setTranslatedText] = useState('');

  useEffect(() => {
    const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', () => {
      setKeyboardVisible(true);
    });
    const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
      setKeyboardVisible(false);
    });

    return () => {
      keyboardDidHideListener.remove();
      keyboardDidShowListener.remove();
    };
  }, []);

  const handleGalleryPhoto = async () => {
    await launchImageLibrary({}, (response) => {
      console.log(response);
      if (!response.didCancel) {
        console.log(response.assets[0]);
        setPhoto(response.assets[0]);
      }
    });
  };

  const handleCameraPhoto = async () => {
    await launchCamera({}, (response) => {
      if (!response.didCancel) {
        console.log(response.assets[0]);
        setPhoto(response.assets[0]);
      }
    });
  };

  const handleExtract = async () => {
    setLoading(true);

    try {
      const user = await Auth.currentAuthenticatedUser();
      const filePath = user.username + '/' + photo.fileName;
      if (photo) {
        const response = await fetch(photo.uri);

        const blob = await response.blob();
        await Storage.put(filePath, blob, {
          contentType: 'image/jpeg',
        });
      }

      const body = {
        filePath: filePath,
        operation: ocrOption,
        targetLanguage: language,
        text: '-',
      };
      console.log(body);

      const res = await API.post(api, path, {body: body});
      setLoading(false);
      console.log(res);
      setExtractedText(res);
    }
    catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  const handleTranslate = async () => {
    setLoading(true);

    try {
      const body = {
        filePath: '-',
        operation: 'Translate',
        targetLanguage: language,
        text: extractedText,
      };
      console.log(body);

      const res = await API.post(api, path, {body: body});
      setLoading(false);
      console.log(res);
      setTranslatedText(res);
    }
    catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  return (
    <>
      <StatusBar barStyle="dark-content" />
        <ImageUploader
          handleGalleryPhoto={handleGalleryPhoto}
          handleCameraPhoto={handleCameraPhoto}
          photo={photo}
        />

        <TextInput
          style={isKeyboardVisible ? styles.textInput(225) : styles.textInput(335)}
          onChangeText={setExtractedText}
          value={extractedText}
          multiline={true}
        />

        <TextInput
          style={styles.textInput(425)}
          onChangeText={() => {}}
          value={translateText}
          multiline={true}
        />

        {!isKeyboardVisible &&
        <>
          <View style={styles.extractText}>
            <OcrSelector setOcrOption={setOcrOption} />
            <ActivityIndicator animating={loading} size="large" color="#a5d3f2" />
            <TouchableOpacity
              onPress={handleExtract}
              style={styles.button}
              disabled={loading}>
              <Text style={loading ? styles.buttonText('white') : styles.buttonText('white')}>
                Extract text
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.translateText}>
            <LanguageSelector setLanguage={setLanguage} />
            <TouchableOpacity
              onPress={handleTranslate}
              style={styles.button}
              disabled={loading || extractedText === '' ? true : false}>
              <Text style={loading || extractedText === '' ? styles.buttonText('#c2c8cc') : styles.buttonText('white')}>
                Translate text
              </Text>
            </TouchableOpacity>
          </View>
        </>
        }
    </>
  );
};

const styles = StyleSheet.create({
  extractText: {
    position: 'absolute',
    right: 30,
    left: 30,
    bottom: 55,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  translateText: {
    position: 'absolute',
    right: 30,
    left: 30,
    bottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    borderRadius: 5,
    width: 130,
    padding: 10,
    backgroundColor: 'gray',
  },
  buttonText: (color) => {
    return {
      color: color,
      textAlign: 'center',
    };
  },
  textInput: (topValue) => {
    return {
      position: 'absolute',
      alignSelf: 'center',
      top: topValue,
      borderRadius: 5,
      borderWidth: 2,
      borderColor: 'gray',
      backgroundColor: 'white',
      height: 80,
      width: 340,
      margin: 8,
      padding: 10,
      fontSize: 18,
    };
  },
});

export default HomeScreen;
