/* eslint-disable prettier/prettier */
import React, {useState} from 'react';

import {
  ActivityIndicator,
  Button,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import {API, Auth, Storage} from 'aws-amplify';
import {launchImageLibrary, launchCamera} from 'react-native-image-picker';

import ImageUploader from './components/image-uploader';
import LanguageSelector from './components/language-selector';
import OcrSelector from './components/ocr-selector';

const myAPI = 'api0a629dfb';
const path = '/translate';

const HomeScreen = () => {

  const [photo, setPhoto] = useState(null);
  const [language, setLanguage] = useState('');
  const [ocrOption, setOcrOption] = useState('');
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState('');

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

  const handleUploadAndInitiate = async () => {
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
        ocrOption: ocrOption,
        language: language,
      };
      console.log(body);

      const res = await API.post(myAPI, path, {body: body});
      setLoading(false);
      console.log(res);
      setOutput(res);
    }
    catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  return (
    <>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView>

        <ActivityIndicator animating={loading} size="large" color="#000000" />
        <View style={styles.space} />

        <ImageUploader
          handleGalleryPhoto={handleGalleryPhoto}
          handleCameraPhoto={handleCameraPhoto}
          photo={photo}
        />
        <View style={styles.space} />

        <LanguageSelector setLanguage={setLanguage} />
        <View style={styles.space} />

        <OcrSelector setOcrOption={setOcrOption} />
        <View style={styles.space} />

        <Button title="Upload and initiate" onPress={handleUploadAndInitiate} />
        <View style={styles.space} />

        <Text>{output}</Text>
      </SafeAreaView>
    </>
  );
};

const styles = StyleSheet.create({
  space: {
    width: 20,
    height: 20,
  },
});

export default HomeScreen;
