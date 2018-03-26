package com.reactathon.notow;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.rekognition.AmazonRekognition;
import com.amazonaws.services.rekognition.AmazonRekognitionClientBuilder;
import com.amazonaws.services.rekognition.model.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.JSONObject;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.util.*;
import java.util.function.Function;
import java.util.regex.Pattern;

public class TextRecognitionHandler implements RequestHandler<Map<String, Object>, TextRecognitionHandler.ResponseMessage> {
//    private List<Rule> regexlist = new ArrayList<Rule>() {{
//        add(new Rule("[a-z \\-]*(no parking|stopping)[a-z ]*",
//                f -> new ResponseMessage(false, "No parking here", f)));
//        add(new Rule("(no parking|stopping) (\\d{1,2})(am|pm)? to (\\d{1,2}) (am|pm)?",
//                f -> new ResponseMessage(noParkingTimeRange.apply(f), "No parking from to", f)));
//        add(new Rule("(one|1|two|2|three|3|four|4|five|5) hour parking (\\d{1,2}) ?(am|pm)? ?- ?(\\d{1,2}) ?(am|pm)?",
//                f -> new ResponseMessage(yesParkingTimeRange.apply(f), "hour parking from to", f)));
//    }};

    List<String> signStart = Arrays.asList("no parking, no stopping tow-away\d hour parking)
    final Function<String, Boolean> noParkingTimeRange = f -> false;
    final Function<String, Boolean> yesParkingTimeRange = f -> true;


    @Override
    public ResponseMessage handleRequest(Map<String, Object> request, Context context) {
        String image = (String) request.get("image");
        String time = (String) request.get("time");
        context.getLogger().log("Input image length " + image.length() + "\n");

        // Create Rekognition client using the parameters available form the runtime context
        AmazonRekognition rekognitionClient =
                AmazonRekognitionClientBuilder.defaultClient();

        if (signsCount(rekognitionClient, image) > 0){
            String signText = detectText(rekognitionClient, image);
            JSONObject json;
            boolean canPark;
            String details;
            try{
                context.getLogger().log("Calling function \n");
                json = postRequest(signText, time, context);
            }catch(Exception e){
                throw new RuntimeException(e);
            }
            return new ResponseMessage(Boolean.valueOf((String)json.get("canPark")), (String)json.get("details"), true, signText);
        }
        else {
            return new ResponseMessage(false, null, false, null);
        }

//        Optional<Rule> optional = regexlist.stream().filter(r -> r.pattern.asPredicate().test(signText)).findFirst();
//        if (optional.isPresent()) {
//            // Return the result (will be serialised to JSON)
//            return optional.get().function.apply(signText);
//        } else {
//            return new ResponseMessage(false, "Not hot dog", signText);
//        }
    }

    private List<String> splitSign(String signText){
        List<String> result = new ArrayList<>();
        Scanner sr = new Scanner(signText);
        Pattern p = Pattern.compile("\"(no parking|stopping) (\\\\d{1,2})(am|pm)? to (\\\\d{1,2}) (am|pm).*");
        while(sr.hasNext(p))
        {
            result.add(sr.next(p));
        }
        sr.close();
        return result;
    }

    private String detectText(AmazonRekognition rekognitionClient, String image){
        final StringBuilder result = new StringBuilder();
        // Create a Rekognition request
        DetectTextRequest request = new DetectTextRequest()
                .withImage(new Image().withBytes(ByteBuffer.wrap(Base64.getMimeDecoder().decode(image))));

        // Call the Rekognition Service
        DetectTextResult response = rekognitionClient.detectText(request);
        response.getTextDetections().stream()
                .filter(d -> d.getType().equals("LINE")) //&& d.getConfidence() > 85)
                .forEachOrdered(d -> result.append(" " + d.getDetectedText()));

        return result.toString().trim().toUpperCase();
    }

    private long signsCount(AmazonRekognition rekognitionClient, String image){
        // Create a Rekognition request
        DetectLabelsRequest request = new DetectLabelsRequest()
                .withImage(new Image().withBytes(ByteBuffer.wrap(Base64.getMimeDecoder().decode(image))));

        // Call the Rekognition Service
        DetectLabelsResult response = rekognitionClient.detectLabels(request);
        return response.getLabels().stream()
                .filter(l -> l.getName().equalsIgnoreCase("sign")
                        || l.getName().equalsIgnoreCase("license plate")
                        || l.getName().equalsIgnoreCase("street sign")
                        || l.getName().equalsIgnoreCase("parking sign")
                )
                .count();
    }

    private JSONObject postRequest(String text, String time, Context context) throws Exception {
        JSONObject result = null;
        CloseableHttpClient httpclient = HttpClients.createDefault();
        try {
            HttpPost httppost = new HttpPost("https://qtbk2103p3.execute-api.us-west-2.amazonaws.com/api/parse");

            httppost.setEntity(new StringEntity("{\"message\":\"" + text + "\",\"time\":\"" + time + "\"}",
                    ContentType.create("application/json")));

            //Execute and get the response.
            HttpResponse response = httpclient.execute(httppost);
            context.getLogger().log("response status" + response.getStatusLine().getStatusCode() + "\n");

            HttpEntity entity = response.getEntity();

            if (entity != null) {
                BufferedReader rd = new BufferedReader(new InputStreamReader(entity.getContent()));
                String line = "";
                while ((line = rd.readLine()) != null) {
                    //Parse our JSON response
                    JSONParser j = new JSONParser();
                    JSONObject o = (JSONObject)j.parse(line);
                    //Map response = (Map)o.get("response");

                    context.getLogger().log("response body" + o.toJSONString() + "\n");
                    result = o;
                }


            }
        }catch(Exception e){
            context.getLogger().log(e.getMessage());
            throw new RuntimeException();
        }finally {
            httpclient.close();
            return result;
        }
    }


    public class Rule {
        Pattern pattern;
        Function<String, ResponseMessage> function;

        public Rule(String regex, Function<String, ResponseMessage> function) {
            this.pattern = Pattern.compile(regex);
            this.function = function;
        }
    }

    public class ResponseMessage {
        boolean canPark;
        String details;
        String signText;
        boolean isSign;

        public ResponseMessage() {

        }

        public ResponseMessage(boolean canPark, String details, boolean isSign, String signText) {
            this.canPark = canPark;
            this.details = details;
            this.signText = signText;
            this.isSign = isSign;
        }

        public boolean isSign() {
            return isSign;
        }

        public ResponseMessage setSign(boolean sign) {
            isSign = sign;
            return this;
        }

        public boolean isCanPark() {
            return canPark;
        }

        public ResponseMessage setCanPark(boolean canPark) {
            this.canPark = canPark;
            return this;
        }

        public String getDetails() {
            return details;
        }

        public ResponseMessage setDetails(String details) {
            this.details = details;
            return this;
        }

        public String getSignText() {
            return signText;
        }

        public ResponseMessage setSignText(String signText) {
            this.signText = signText;
            return this;
        }
    }

    public class RquestMessage {
        String message;
        String time;

        public String getMessage() {
            return message;
        }

        public RquestMessage setMessage(String message) {
            this.message = message;
            return this;
        }

        public String getTime() {
            return time;
        }

        public RquestMessage setTime(String time) {
            this.time = time;
            return this;
        }
    }

}
